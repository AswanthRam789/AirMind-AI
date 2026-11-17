
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import PredictionRequest, PredictionResponse
from explainability import explain_prediction


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="AirMind AI API",
    description="Context-Aware Intelligent Comfort System",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).parent
    / "models"
    / "airmind_model.joblib"
)

FEATURE_NAMES = [
    "temperature",
    "humidity",
    "occupied",
    "comfort_preference",
]

PREFERENCE_MAP = {
    "Energy-conscious": 0,
    "Balanced": 1,
    "More airflow": 2,
}

MODEL_READY = False
MODEL_ERROR = None
model = None


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

def extract_model(loaded_model):

    if not isinstance(loaded_model, dict):
        return loaded_model

    print("Saved model dictionary keys:", loaded_model.keys())

    # Common model keys
    preferred_keys = [
        "model",
        "classifier",
        "random_forest",
        "rf",
        "pipeline",
        "best_model",
    ]

    for key in preferred_keys:
        candidate = loaded_model.get(key)

        if (
            candidate is not None
            and hasattr(candidate, "predict")
            and hasattr(candidate, "predict_proba")
        ):
            print(f"Model extracted using key: {key}")
            return candidate

    # Search all dictionary values
    for key, candidate in loaded_model.items():

        if (
            hasattr(candidate, "predict")
            and hasattr(candidate, "predict_proba")
        ):
            print(f"Model extracted using key: {key}")
            return candidate

    raise ValueError(
        "No prediction model found inside saved dictionary. "
        f"Available keys: {list(loaded_model.keys())}"
    )


try:

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    loaded_model = joblib.load(MODEL_PATH)

    model = extract_model(loaded_model)

    # Validate feature order when available
    if hasattr(model, "feature_names_in_"):

        saved_features = list(model.feature_names_in_)

        if saved_features != FEATURE_NAMES:
            raise ValueError(
                f"Feature mismatch. Model: {saved_features}, "
                f"API: {FEATURE_NAMES}"
            )

    MODEL_READY = True

    print("AirMind AI model loaded successfully!")
    print("Model type:", type(model).__name__)

except Exception as error:

    MODEL_READY = False
    MODEL_ERROR = str(error)

    print("Model loading failed:", MODEL_ERROR)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health_check():

    return {
        "status": "online",
        "model_loaded": MODEL_READY,
        "model_name": "Random Forest",
        "version": "2.0.0",
    }


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

@app.post(
    "/api/predict",
    response_model=PredictionResponse,
)
def predict(request: PredictionRequest):

    if not MODEL_READY:
        raise HTTPException(
            status_code=503,
            detail=f"Model unavailable: {MODEL_ERROR}",
        )

    try:

        # Prepare input
        input_data = pd.DataFrame(
            [
                [
                    request.temperature,
                    request.humidity,
                    int(request.occupied),
                    PREFERENCE_MAP[
                        request.comfort_preference
                    ],
                ]
            ],
            columns=FEATURE_NAMES,
        )

        # ML prediction
        ml_prediction = str(
            model.predict(input_data)[0]
        )

        # Model scores
        probabilities = model.predict_proba(
            input_data
        )[0]

        model_scores = {
            str(label): round(
                float(score) * 100,
                2,
            )
            for label, score in zip(
                model.classes_,
                probabilities,
            )
        }

        # SHAP explanation
        shap_explanation = explain_prediction(
            model=model,
            temperature=request.temperature,
            humidity=request.humidity,
            occupied=request.occupied,
            preference=request.comfort_preference,
        )

        # --------------------------------------------------
        # DECISION LOGIC
        # --------------------------------------------------

        explanation = []

        if request.manual_override:

            final_recommendation = request.manual_speed
            control_mode = "Manual Override"

            explanation.append(
                "Manual override is active."
            )

            explanation.append(
                f"User-selected speed: "
                f"{request.manual_speed}."
            )

        elif not request.occupied:

            final_recommendation = "Off"
            control_mode = "Vacancy Safety"

            explanation.append(
                "Room is unoccupied; recommendation is Off."
            )

        else:

            final_recommendation = ml_prediction
            control_mode = "Automatic ML Mode"

            explanation.append(
                f"Random Forest predicted {ml_prediction}."
            )

            explanation.append(
                f"Temperature: {request.temperature}°C."
            )

            explanation.append(
                f"Humidity: {request.humidity}%."
            )

            explanation.append(
                f"Comfort preference: "
                f"{request.comfort_preference}."
            )

        # SHAP summary
        if shap_explanation:

            strongest = shap_explanation[0]

            explanation.append(
                "Highest absolute SHAP contribution: "
                f"{strongest['feature']} "
                f"({strongest['impact']:+.4f})."
            )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return PredictionResponse(
            ml_prediction=ml_prediction,
            final_recommendation=final_recommendation,
            model_scores=model_scores,
            temperature=request.temperature,
            humidity=request.humidity,
            occupied=request.occupied,
            control_mode=control_mode,
            explanation=explanation,
            model_status="Random Forest + SHAP",
            shap_explanation=shap_explanation,
        )

    except HTTPException:
        raise

    except Exception as error:

        print("Prediction error:", str(error))

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}",
        )
