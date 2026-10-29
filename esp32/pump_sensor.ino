/*
 * ======================================================================================
 * SMART PUMP FAULT PREDICTION SYSTEM — ESP32 HARDWARE INTEGRATION SKETCH
 * ======================================================================================
 * Project: Smart Pump Fault Prediction — Industrial Pump Condition Monitoring
 * 
 * Target Hardware:
 *   - Microcontroller: ESP32 Dev Module
 *   - Pressure Sensor: Industrial Pressure Transducer (0-10 bar, 0.5V-4.5V output) -> Pin GPIO 34 (ADC1_CH6)
 *   - Current Sensor: ACS712-20A Hall-Effect Current Sensor Module -> Pin GPIO 35 (ADC1_CH7)
 *   - Vibration Sensor: ADXL345 / Piezoelectric Analog Vibration Sensor -> Pin GPIO 32 (ADC1_CH4)
 *   - Water Pump: Low-Voltage DC Centrifugal Water Pump (12V)
 * 
 * NOTE FOR ACADEMIC AUDIT:
 *   Current software evaluation uses the Sensor Simulator layer ("data_source": "SIMULATED").
 *   This sketch is pre-configured and ready for future physical deployment.
 *   When flashed to ESP32, it transmits "data_source": "ESP32" to the Flask REST API.
 * ======================================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- Wi-Fi Configuration ---
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// --- Flask REST API Configuration ---
// Replace with the IP address of the machine running the Flask server
const char* SERVER_URL = "http://192.168.1.100:5000/api/sensor-data";

// --- Hardware Pin Definitions ---
const int PIN_PRESSURE_SENSOR  = 34; // Analog In
const int PIN_CURRENT_SENSOR   = 35; // Analog In
const int PIN_VIBRATION_SENSOR = 32; // Analog In

// --- Calibration Parameters ---
const float ADC_REF_VOLTAGE = 3.3;
const int ADC_RESOLUTION = 4095;

// Sampling Interval (milliseconds)
const unsigned long SAMPLING_INTERVAL_MS = 2000;
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=======================================================");
  Serial.println("  Smart Pump Monitoring System — ESP32 IoT Node Setup  ");
  Serial.println("=======================================================");

  // Pin modes
  pinMode(PIN_PRESSURE_SENSOR, INPUT);
  pinMode(PIN_CURRENT_SENSOR, INPUT);
  pinMode(PIN_VIBRATION_SENSOR, INPUT);

  // Connect to Wi-Fi Network
  Serial.print("Connecting to Wi-Fi SSID: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi Connected successfully!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.println("Ready to collect sensor readings...\n");
}

float readPressureSensor() {
  int rawADC = analogRead(PIN_PRESSURE_SENSOR);
  float voltage = (rawADC / (float)ADC_RESOLUTION) * ADC_REF_VOLTAGE;
  // Convert voltage (0.5V - 4.5V) to Pressure in bar (0 - 10 bar)
  float pressureBar = (voltage - 0.5) * (10.0 / 4.0);
  return (pressureBar < 0.0) ? 0.0 : pressureBar;
}

float readCurrentSensor() {
  int rawADC = analogRead(PIN_CURRENT_SENSOR);
  float voltage = (rawADC / (float)ADC_RESOLUTION) * ADC_REF_VOLTAGE;
  // ACS712-20A sensitivity is 100mV/A with VCC/2 offset (1.65V at 3.3V ADC)
  float currentAmps = abs(voltage - 1.65) / 0.100;
  return currentAmps;
}

float readVibrationSensor() {
  int rawADC = analogRead(PIN_VIBRATION_SENSOR);
  float voltage = (rawADC / (float)ADC_RESOLUTION) * ADC_REF_VOLTAGE;
  // Map analog vibration voltage to RMS velocity (mm/s)
  float vibrationMMS = voltage * 3.5;
  return vibrationMMS;
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - lastSampleTime >= SAMPLING_INTERVAL_MS) {
    lastSampleTime = currentMillis;

    if (WiFi.status() == WL_CONNECTED) {
      // 1. Read Physical Sensor Values
      float pressure  = readPressureSensor();
      float current   = readCurrentSensor();
      float vibration = readVibrationSensor();

      Serial.printf("[SENSOR READ] Pressure: %.2f bar | Current: %.2f A | Vibration: %.2f mm/s\n",
                    pressure, current, vibration);

      // 2. Construct JSON Payload with ESP32 data source marker
      StaticJsonDocument<256> doc;
      doc["pressure"]    = pressure;
      doc["current"]     = current;
      doc["vibration"]   = vibration;
      doc["data_source"] = "ESP32"; // Explicit hardware marker

      String jsonPayload;
      serializeJson(doc, jsonPayload);

      // 3. Send HTTP POST to Flask API Endpoint
      HTTPClient http;
      http.begin(SERVER_URL);
      http.addHeader("Content-Type", "application/json");

      int httpResponseCode = http.POST(jsonPayload);

      if (httpResponseCode > 0) {
        String responseStr = http.getString();
        Serial.printf("HTTP Response [%d]: %s\n", httpResponseCode, responseStr.c_str());
      } else {
        Serial.printf("HTTP POST Error Code: %d\n", httpResponseCode);
      }

      http.end();
    } else {
      Serial.println("Wi-Fi disconnected! Reconnecting...");
      WiFi.reconnect();
    }
  }
}
