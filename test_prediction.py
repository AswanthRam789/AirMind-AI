
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "models" / "airmind_model.joblib"

# Load the saved model and metadata
saved = joblib.load(MODEL_PATH)
model = saved["model"]
features = saved["features"]

# Example room conditions
room = pd.DataFrame([{
    "temperature": 32.0,
    "humidity": 70.0,
    "occupied": 1,
    "comfort_preference": 1,
}])[features]

prediction = model.predict(room)[0]
probabilities = model.predict_proba(room)[0]

print("\n===== AirMind AI Prediction =====")
print(f"Temperature: {room.iloc[0]['temperature']} °C")
print(f"Humidity: {room.iloc[0]['humidity']}%")
print("Occupancy: Occupied")
print(f"Recommended fan speed: {prediction}")
print("\nModel class probabilities:")

for label, probability in zip(model.classes_, probabilities):
    print(f"{label}: {probability:.1%}")
