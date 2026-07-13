import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("Step 1: Loading historical soil data...")
try:
    # Load the CSV file
    df = pd.read_csv("historical_soil_data.csv")
except FileNotFoundError:
    print("Error: Could not find 'historical_soil_data.csv'. Ensure it is in the same folder.")
    exit()

print("Step 2: Preparing features (X) and labels (y)...")
# X contains the sensor numbers, y contains the text advisory
X = df[['Temperature', 'Humidity', 'Moisture', 'HeatIndex']]
y = df['Advisory_Action']

# Split the data: 80% for training the brain, 20% for testing its accuracy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Step 3: Training the Random Forest Classifier...")
# Initialize the model with 100 'decision trees'
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model on the data
rf_model.fit(X_train, y_train)

print("Step 4: Evaluating AI accuracy...")
# Ask the model to predict the 20% of data it hasn't seen yet
y_pred = rf_model.predict(X_test)

# Calculate how many it got right
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy * 100:.2f}%\n")
print("Detailed Classification Report:")
print(classification_report(y_test, y_pred))

print("Step 5: Exporting the trained brain...")
# Save the trained model as a file so the real-time rover script can use it
model_filename = "soil_rf_model.pkl"
joblib.dump(rf_model, model_filename)

print(f"Success! Model saved as '{model_filename}'.")
print("You can now start your Arduino and run your real-time prediction script!")
