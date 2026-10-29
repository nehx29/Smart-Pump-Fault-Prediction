import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input

def build_model(input_shape=(3,), num_classes=5, learning_rate=0.001):
    """
    Builds and compiles the Deep Neural Network (DNN) classifier.
    
    Architecture:
    Input (3 features: pressure, current, vibration)
      │
      ├── Dense(64, ReLU) + BatchNormalization + Dropout(0.2)
      ├── Dense(32, ReLU) + BatchNormalization + Dropout(0.15)
      ├── Dense(16, ReLU)
      └── Dense(5, Softmax) -> Multiclass Output
    """
    model = Sequential([
        Input(shape=input_shape, name="sensor_input"),
        Dense(64, activation='relu', kernel_initializer='he_normal', name="dense_1"),
        BatchNormalization(name="bn_1"),
        Dropout(0.2, name="dropout_1"),
        
        Dense(32, activation='relu', kernel_initializer='he_normal', name="dense_2"),
        BatchNormalization(name="bn_2"),
        Dropout(0.15, name="dropout_2"),
        
        Dense(16, activation='relu', kernel_initializer='he_normal', name="dense_3"),
        Dense(num_classes, activation='softmax', name="output_softmax")
    ], name="Smart_Pump_DNN_Classifier")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

if __name__ == '__main__':
    model = build_model()
    model.summary()
