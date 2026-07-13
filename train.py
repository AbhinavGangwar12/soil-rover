import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load your historical soil dataset
# Ensure your CSV has columns matching your sensors exactly
df = pd.read_csv("historical_soil_data.csv")

# 2. Split features (X) and target/advisory (y)
X = df[['Temperature', 'Humidity', 'Moisture', 'HeatIndex']]
y = df['Advisory_Action'] 

# 3. Train the Random Forest
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# 4. Save the "Brain" to a file for the real-time script to use
joblib.dump(clf, "soil_rf_model.pkl")
print("Model saved successfully!")
