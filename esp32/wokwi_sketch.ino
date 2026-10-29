/*
 * =============================================================================
 * Smart Pump Monitoring — ESP32 Wokwi Simulator Sketch
 * =============================================================================
 *
 * Sends sensor readings (GPIO 34/35/32) to the Flask backend every 3 seconds.
 * Readings are labelled data_source: "WOKWI_SIMULATED".
 *
 * BEFORE RUNNING:
 *   1. Start Flask:  python app.py  (in backend/)
 *   2. Start tunnel: cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:5000
 *   3. Copy the https://xxxx-yyyy-zzzz.trycloudflare.com URL printed by cloudflared.
 *   4. Paste it into SERVER_URL below (both constants), replacing the placeholder.
 *   5. Save this file, then Run the simulation in Wokwi.
 *
 * Quick tunnel URLs expire when cloudflared restarts. Update both constants and
 * restart the Wokwi simulation each session.
 * See TUNNEL_SETUP.md for the full workflow and troubleshooting guide.
 * =============================================================================
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

/* ── Wi-Fi ─────────────────────────────────────────────────────────────────
 * Wokwi virtual AP:  SSID = "Wokwi-GUEST",  password = "" (empty string).
 * Do NOT supply a channel number — the virtual AP does not broadcast on a
 * fixed channel and a channel hint causes WL_CONNECTED to never be reached.
 */
static const char* WIFI_SSID = "Wokwi-GUEST";
static const char* WIFI_PASS = "";             // empty — no password

/* ── Cloudflare tunnel URL ─────────────────────────────────────────────────
 * Replace the placeholder with the URL printed by cloudflared each session.
 * Both constants must point to the same tunnel origin.
 * Leave empty ("") if you have not started a tunnel yet.
 */
static const char* CLOUDFLARE_HOST = "https://aquarium-indoor-affected-likes.trycloudflare.com";  // update each session
static const char* SERVER_URL      = "https://aquarium-indoor-affected-likes.trycloudflare.com/api/sensor-data";  // update each session

/* ── GPIO mapping ──────────────────────────────────────────────────────────
 * GPIO 34 → Pressure sensor   (ADC1_CH6, input-only)
 * GPIO 35 → Motor current     (ADC1_CH7, input-only)
 * GPIO 32 → Vibration sensor  (ADC1_CH4)
 *
 * Physical unit conversion:  physical = (ADC_raw / 4095) * MAX_VALUE
 *   PRESSURE_MAX  = 15.0 bar     → slider 25%  ≈ 3.8 bar   (Normal centre)
 *   CURRENT_MAX   = 25.0 A       → slider 20%  ≈ 5.0 A     (Normal centre)
 *   VIBRATION_MAX = 20.0 mm/s    → slider  6%  ≈ 1.2 mm/s  (Normal centre)
 *
 * Slider positions for each fault condition:
 *   Normal            P ~25%  C ~20%  V  ~6%
 *   High Pressure     P ~45%  C ~26%  V ~14%
 *   Overcurrent       P ~22%  C ~37%  V ~17%
 *   Excess Vibration  P ~24%  C ~22%  V ~34%
 *   Combined Fault    P  ~8%  C ~34%  V ~38%
 */
static const int   PIN_PRESSURE     = 34;
static const int   PIN_CURRENT      = 35;
static const int   PIN_VIBRATION    = 32;
static const float ADC_MAX          = 4095.0f;
static const float PRESSURE_MAX     = 15.0f;
static const float CURRENT_MAX      = 25.0f;
static const float VIBRATION_MAX    = 20.0f;

/* ── Timing ────────────────────────────────────────────────────────────── */
static const unsigned long SEND_INTERVAL_MS  = 3000;   // ms between readings
static const unsigned long WIFI_POLL_MS      = 500;    // ms between status polls
static const int           WIFI_MAX_ATTEMPTS = 20;     // 20 × 500 ms = 10 s max
static const int           HTTP_TIMEOUT_MS   = 15000;

unsigned long lastSendTime = 0;

/* ─────────────────────────────────────────────────────────────────────────
 * adcToPhysical()
 * Converts a 12-bit ADC reading to a physical unit value.
 */
float adcToPhysical(int raw, float maximum) {
  raw = constrain(raw, 0, 4095);
  return (raw / ADC_MAX) * maximum;
}

/* ─────────────────────────────────────────────────────────────────────────
 * connectWiFi()
 *
 * Connects to Wokwi-GUEST using bounded polling (no infinite loop).
 * Key fix: WiFi.begin() is called WITHOUT a channel argument.
 *          Passing a channel hint (e.g. the old ", 6") restricts the ESP32
 *          driver to scan only that channel; the Wokwi virtual AP does not
 *          broadcast on a fixed channel, so WL_CONNECTED was never reached.
 *
 * Returns true on success, false after WIFI_MAX_ATTEMPTS polls.
 */
bool connectWiFi() {
  Serial.println("[WiFi] Starting connection to Wokwi-GUEST...");
  Serial.printf("[WiFi] SSID: %s | Password: %s\n",
                WIFI_SSID,
                (WIFI_PASS[0] == '\0') ? "(empty)" : "***");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true);         // clear any stale association
  delay(100);

  // Begin WITHOUT a channel hint — critical for Wokwi virtual AP
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  for (int attempt = 1; attempt <= WIFI_MAX_ATTEMPTS; attempt++) {
    wl_status_t status = WiFi.status();

    if (status == WL_CONNECTED) {
      Serial.println();
      Serial.println("[WiFi] Connected successfully.");
      Serial.printf("[WiFi] IP address : %s\n", WiFi.localIP().toString().c_str());
      Serial.printf("[WiFi] Signal (RSSI): %d dBm\n", WiFi.RSSI());
      return true;
    }

    // Print status code so the user can see progress
    Serial.printf("[WiFi] Attempt %d/%d — status %d",
                  attempt, WIFI_MAX_ATTEMPTS, (int)status);

    // Human-readable status
    switch (status) {
      case WL_IDLE_STATUS:     Serial.print(" (IDLE)");          break;
      case WL_NO_SSID_AVAIL:   Serial.print(" (SSID NOT FOUND)"); break;
      case WL_CONNECT_FAILED:  Serial.print(" (CONNECT FAILED)"); break;
      case WL_DISCONNECTED:    Serial.print(" (DISCONNECTED)");   break;
      default:                 break;
    }
    Serial.println();
    delay(WIFI_POLL_MS);
  }

  Serial.println("[WiFi][ERROR] Could not connect within timeout.");
  Serial.println("[WiFi][ERROR] Ensure SSID is 'Wokwi-GUEST' and password is empty.");
  Serial.println("[WiFi][ERROR] Retry in 5 s...");
  return false;
}

/* ─────────────────────────────────────────────────────────────────────────
 * isTunnelUrlSet()
 *
 * Returns false if SERVER_URL is empty or still contains the placeholder
 * text, so the loop can skip HTTP attempts with a clear message instead of
 * silently failing on a DNS lookup for a stale URL.
 */
bool isTunnelUrlSet() {
  if (SERVER_URL[0] == '\0') return false;
  // Reject the example placeholder inserted by the comment block
  if (strstr(SERVER_URL, "xxxx") != nullptr) return false;
  if (strstr(SERVER_URL, "trycloudflare") == nullptr) return false;
  return true;
}

/* ─────────────────────────────────────────────────────────────────────────
 * setup()
 */
void setup() {
  Serial.begin(115200);
  delay(1000);

  analogReadResolution(12);

  Serial.println();
  Serial.println("==========================================");
  Serial.println(" Smart Pump Monitoring");
  Serial.println(" ESP32 Wokwi simulator");
  Serial.println(" Data source: WOKWI_SIMULATED");
  Serial.println("==========================================");

  // Report tunnel URL status at startup
  if (!isTunnelUrlSet()) {
    Serial.println();
    Serial.println("[CONFIG] SERVER_URL is not set or still contains placeholder.");
    Serial.println("[CONFIG] Sensor readings will be read and printed locally,");
    Serial.println("[CONFIG] but no data will be sent to the backend.");
    Serial.println("[CONFIG] To send data:");
    Serial.println("[CONFIG]   1. Run: cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:5000");
    Serial.println("[CONFIG]   2. Copy the https://xxxx-yyyy-zzzz.trycloudflare.com URL.");
    Serial.println("[CONFIG]   3. Paste it into SERVER_URL in this sketch.");
    Serial.println("[CONFIG]   4. Restart this simulation.");
  } else {
    Serial.printf("[CONFIG] Tunnel endpoint: %s\n", SERVER_URL);
  }

  // Connect to Wi-Fi (required even if SERVER_URL is empty — validates AP)
  if (!connectWiFi()) {
    Serial.println("[WARN] Starting without Wi-Fi. Will retry each loop.");
  }
}

/* ─────────────────────────────────────────────────────────────────────────
 * loop()
 */
void loop() {
  // ── Wi-Fi reconnect (bounded, not infinite) ──
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Connection lost. Attempting reconnect...");
    if (!connectWiFi()) {
      Serial.println("[WiFi] Reconnect failed. Waiting 5 s before next attempt.");
      delay(5000);
      return;
    }
  }

  // ── Rate limiting ──
  if (millis() - lastSendTime < SEND_INTERVAL_MS) {
    delay(10);
    return;
  }
  lastSendTime = millis();

  // ── Read sensor ADC values (GPIO 34/35/32) ──
  int pressureADC  = analogRead(PIN_PRESSURE);
  int currentADC   = analogRead(PIN_CURRENT);
  int vibrationADC = analogRead(PIN_VIBRATION);

  float pressure  = adcToPhysical(pressureADC,  PRESSURE_MAX);
  float current   = adcToPhysical(currentADC,   CURRENT_MAX);
  float vibration = adcToPhysical(vibrationADC, VIBRATION_MAX);

  Serial.println("\n------------------------------------------");
  Serial.printf("[SENSOR] Pressure  ADC=%4d → %6.3f bar\n",  pressureADC,  pressure);
  Serial.printf("[SENSOR] Current   ADC=%4d → %6.3f A\n",    currentADC,   current);
  Serial.printf("[SENSOR] Vibration ADC=%4d → %6.3f mm/s\n", vibrationADC, vibration);

  // ── Skip HTTP if tunnel URL is not configured ──
  if (!isTunnelUrlSet()) {
    Serial.println("[HTTP] Skipping send — SERVER_URL not configured.");
    Serial.println("[HTTP] Update SERVER_URL with a fresh tunnel URL and restart.");
    Serial.println("------------------------------------------");
    return;
  }

  // ── Build JSON payload ──
  StaticJsonDocument<256> doc;
  doc["pump_id"]     = "PUMP-001";
  doc["pressure"]    = pressure;
  doc["current"]     = current;
  doc["vibration"]   = vibration;
  doc["data_source"] = "WOKWI_SIMULATED";

  String requestBody;
  serializeJson(doc, requestBody);
  Serial.printf("[HTTP] POST %s\n", SERVER_URL);
  Serial.printf("[HTTP] Body: %s\n", requestBody.c_str());

  // ── HTTPS POST ──
  WiFiClientSecure secureClient;
  secureClient.setInsecure();   // skip TLS cert verification (Quick Tunnel)

  HTTPClient http;
  http.setConnectTimeout(10000);
  http.setTimeout(HTTP_TIMEOUT_MS);

  if (!http.begin(secureClient, SERVER_URL)) {
    Serial.println("[HTTP][ERROR] http.begin() failed. Check SERVER_URL format.");
    http.end();
    Serial.println("------------------------------------------");
    return;
  }

  http.addHeader("Content-Type", "application/json");
  http.addHeader("Accept",       "application/json");

  int statusCode = http.POST(requestBody);

  if (statusCode > 0) {
    String responseBody = http.getString();
    Serial.printf("[HTTP] Response code: %d\n", statusCode);

    if (statusCode >= 200 && statusCode < 300) {
      Serial.println("[HTTP] SUCCESS — reading stored.");

      // Parse and print prediction result
      StaticJsonDocument<2048> respDoc;
      DeserializationError err = deserializeJson(respDoc, responseBody);
      if (!err) {
        const char* prediction = respDoc["data"]["prediction"] | "unavailable";
        float confidence       = respDoc["data"]["confidence"] | -1.0f;
        Serial.printf("[RESULT] Condition  : %s\n", prediction);
        if (confidence >= 0.0f) {
          Serial.printf("[RESULT] Confidence : %.2f%%\n", confidence * 100.0f);
        }
        const char* stored_ts = respDoc["data"]["timestamp"] | "";
        if (strlen(stored_ts) > 0) {
          Serial.printf("[RESULT] Stored at  : %s\n", stored_ts);
        }
      } else {
        // Print raw response so the user can see what the backend returned
        Serial.printf("[HTTP] Response (raw): %s\n", responseBody.c_str());
      }
    } else {
      Serial.printf("[HTTP][ERROR] Server returned %d.\n", statusCode);
      if (statusCode == 400) Serial.println("[HTTP] Check JSON fields: pressure, current, vibration required.");
      if (statusCode == 404) Serial.println("[HTTP] Wrong path — must end in /api/sensor-data");
      if (statusCode >= 500) Serial.println("[HTTP] Backend error — check Flask logs.");
      Serial.printf("[HTTP] Response (raw): %s\n", responseBody.c_str());
    }
  } else {
    // statusCode <= 0 means the request itself failed (DNS, TCP, TLS)
    Serial.printf("[HTTP][ERROR] Request failed (code %d): %s\n",
                  statusCode, http.errorToString(statusCode).c_str());
    Serial.println("[HTTP] Possible causes:");
    Serial.println("[HTTP]  - Tunnel URL has expired (restart cloudflared, update SERVER_URL)");
    Serial.println("[HTTP]  - Flask backend is not running");
    Serial.println("[HTTP]  - DNS lookup failed (invalid or expired URL)");
  }

  http.end();
  Serial.println("------------------------------------------");
}
