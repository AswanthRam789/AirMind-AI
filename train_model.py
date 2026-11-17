
# train_model.py
# AirMind AI - Initial ML Training Pipeline
# Training labels are simulated rule-based examples, not measured comfort data.

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

DATA_PATH = BASE_DIR / "training_data.csv"
MODEL_PATH = MODEL_DIR / "airmind_model.joblib"

FEATURES = [
    "temperature",
    "humidity",
    "occupied",
    "comfort_preference",
]

CLASSES = ["Off", "Low", "Medium", "High"]


# --------------------------------------------------
# 2. Generate illustrative training data
# --------------------------------------------------
def assign_simulated_label(row):
    """Create a provisional label using documented example rules."""

    if row["occupied"] == 0:
        return "Off"

    # Illustrative comfort-demand score, not a validated
    # physiological comfort or energy model.
    demand = (
        0.65 * (row["temperature"] - 24)
        + 0.035 * (row["humidity"] - 50)
        + 1.0 * row["comfort_preference"]
    )

    if demand < 0.8:
        return "Low"
    elif demand < 3.5:
        return "Medium"
    else:
        return "High"


def generate_dataset(n_samples=5000, random_state=42):
    """Generate reproducible synthetic sensor scenarios."""

    rng = __import__("numpy").random.default_rng(random_state)

    data = pd.DataFrame({
        "temperature": rng.uniform(18, 40, n_samples).round(1),
        "humidity": rng.uniform(20, 95, n_samples).round(1),
        "occupied": rng.integers(0, 2, n_samples),
        # 0 = energy-conscious, 1 = balanced, 2 = prefers more airflow
        "comfort_preference": rng.integers(0, 3, n_samples),
    })

    data["fan_speed"] = data.apply(assign_simulated_label, axis=1)
    return data


# --------------------------------------------------
# 3. Train and evaluate
# --------------------------------------------------
def main():
    data = generate_dataset()

    data.to_csv(DATA_PATH, index=False)

    X = data[FEATURES]
    y = data["fan_speed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\n===== AirMind AI: Model Evaluation =====")
    print(f"Training examples: {len(X_train)}")
    print(f"Testing examples:  {len(X_test)}")
    print(f"Accuracy against simulated labels: "
          f"{accuracy_score(y_test, predictions):.2%}")

    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        labels=CLASSES,
        zero_division=0,
    ))

    print("Confusion matrix (rows=true, columns=predicted):")
    print(confusion_matrix(y_test, predictions, labels=CLASSES))

    print("\nFeature importance:")
    for name, importance in sorted(
        zip(FEATURES, model.feature_importances_),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"{name}: {importance:.3f}")

    # Save model and metadata together.
    joblib.dump(
        {
            "model": model,
            "features": FEATURES,
            "classes": CLASSES,
            "label_source": "synthetic_rule_based",
        },
        MODEL_PATH,
    )

    print(f"\nDataset saved to: {DATA_PATH}")
    print(f"Model saved to:   {MODEL_PATH}")
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
