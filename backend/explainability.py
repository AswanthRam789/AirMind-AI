
import numpy as np
import pandas as pd
import shap

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


def explain_prediction(
    model,
    temperature,
    humidity,
    occupied,
    preference,
):
    input_data = pd.DataFrame(
        [[
            temperature,
            humidity,
            int(occupied),
            PREFERENCE_MAP[preference],
        ]],
        columns=FEATURE_NAMES,
    )

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(input_data)

    prediction = model.predict(input_data)[0]
    class_index = list(model.classes_).index(prediction)

    # Support older and newer SHAP output formats
    if isinstance(shap_values, list):
        contributions = np.asarray(
            shap_values[class_index]
        )[0]

    else:
        values = np.asarray(shap_values)

        if values.ndim == 3:
            contributions = values[0, :, class_index]

        elif values.ndim == 2:
            contributions = values[0]

        else:
            raise ValueError(
                f"Unexpected SHAP shape: {values.shape}"
            )

    results = []

    for feature, impact in zip(
        FEATURE_NAMES,
        contributions,
    ):
        results.append({
            "feature": feature,
            "impact": round(float(impact), 6),
        })

    results.sort(
        key=lambda item: abs(item["impact"]),
        reverse=True,
    )

    return results
