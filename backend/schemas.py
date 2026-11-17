
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temperature: float = Field(ge=18, le=40)
    humidity: float = Field(ge=20, le=95)
    occupied: bool

    comfort_preference: Literal[
        "Energy-conscious",
        "Balanced",
        "More airflow",
    ]

    manual_override: bool = False

    manual_speed: Literal[
        "Off",
        "Low",
        "Medium",
        "High",
    ] = "Medium"


class SHAPContribution(BaseModel):
    feature: str
    impact: float


class PredictionResponse(BaseModel):
    ml_prediction: str
    final_recommendation: str
    model_scores: dict[str, float]

    temperature: float
    humidity: float
    occupied: bool

    control_mode: str
    explanation: list[str]
    model_status: str

    shap_explanation: list[SHAPContribution]
