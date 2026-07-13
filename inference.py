import serial
import joblib
import numpy as np
import time

# ==========================================
# 1. LOAD THE AI MODEL
# ==========================================
# Load your pre-trained Random Forest model
# (Make sure this .pkl file is in the same folder as this script)
try:
    rf_model = joblib.load("soil_rf_model.pkl")
    print("Random Forest model loaded successfully.")
except FileNotFoundError:
    print("Error: 'soil_rf_model.pkl' not found. You need to train and save your model first.")
    exit()

# ==========================================
# 2. CONNECT TO BLUETOOTH
# ==========================================
BLUETOOTH_PORT = "COM5" 
BAUD_RATE = 9600

try:
    bt_serial = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
    print(f"Successfully connected to HC-05 on {BLUETOOTH_PORT}")
except Exception as e:
    print(f"Connection failed: {e}")
    print("Check your Bluetooth settings and ensure the port is correct.")
    exit()

print("Listening for incoming Soil & Weather data... (Press Ctrl+C to stop)")
print("=" * 60)

# ==========================================
# 3. THE REAL-TIME PREDICTION LOOP
# ==========================================
while True:
    try:
        # Check if data is waiting in the Bluetooth buffer
        if bt_serial.in_waiting > 0:
            
            # Read the incoming CSV string from Arduino
            # Example incoming string: "28.50, 45.20, 0, 29.10"
            raw_data = bt_serial.readline().decode('utf-8').strip()
            
            # Skip empty lines or the failsafe "nan" strings
            if not raw_data or "nan" in raw_data:
                continue

            # Convert the CSV string into a list of floats
            features = [float(val) for val in raw_data.split(',')]
            
            # Ensure we received exactly 4 features (Temp, Hum, Moist, HeatIndex)
            if len(features) == 4:
                
                # Reshape for scikit-learn (1 sample, 4 features)
                feature_array = np.array(features).reshape(1, -1)
                
                # Feed into Random Forest for prediction
                prediction = rf_model.predict(feature_array)
                
                # Extract the actual class name (e.g., "Optimal", "Needs Irrigation", "Drought Warning")
                advisory_output = prediction[0]
                
                # Print the live dashboard to the terminal
                print(f"Raw Sensors : Temp={features[0]}°C | Hum={features[1]}% | Moist={features[2]} | HI={features[3]}")
                print(f"AI Advisory : >> {advisory_output} <<")
                print("-" * 60)
                
    except ValueError:
        # Handle cases where the serial data was cut off mid-transmission
        pass
    except KeyboardInterrupt:
        # Safely close the port if you press Ctrl+C
        print("\nShutting down AI brain. Closing connection.")
        bt_serial.close()
        break
