import base64
import os
from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression


@dataclass
class YieldResult:
    predicted_yield_kg_per_ha: float
    note: str


class ModelService:
    def __init__(self):
        self.yield_model = None
        self.weather_model = None

        # Demo disease classes (33). Replace with your real 33-class mapping if available.
        self.disease_classes = [
            "Tomato__Early_blight",
            "Tomato__Late_blight",
            "Tomato__Leaf_Mold",
            "Potato__Early_blight",
            "Potato__Late_blight",
            "Potato__Leaf_Mold",
            "Pepper__Bacterial_spot",
            "Corn__Rust",
            "Corn__Blight",
            "Apple__Scab",
            "Apple__Black_rot",
            "Apple__Cedar_apple_rust",
            "Grape__Black_rot",
            "Grape__Esca__Leaf_disease",
            "Grape__Leaf_blight",
            "Orange__Haunglongbing",
            "Peach__Bacterial_spot",
            "Cherry__Powdery_mildew",
            "Blueberry__Healthy",
            "Strawberry__Healthy",
            "Raspberry__Healthy",
            "Soybean__Healthy",
            "Wheat__Healthy",
            "Rice__Healthy",
            "Barley__Healthy",
            "Oats__Healthy",
            "Cabbage__Healthy",
            "Cauliflower__Healthy",
            "Lettuce__Healthy",
            "Spinach__Healthy",
            "Carrot__Healthy",
            "Beet__Healthy",
            "Sorghum__Healthy",
        ]

    def _ensure_models(self):
        # Build demo models if missing (so app is runnable).
        if self.yield_model is None:
            rng = np.random.default_rng(42)
            X = rng.uniform(low=[50, 0, 10], high=[300, 20, 40], size=(400, 3))
            # Synthetic relation: yield increases with rainfall & temperature (until a point), decreases with pesticide noise.
            y = (
                0.8 * X[:, 0] +
                12 * X[:, 2] -
                40 * X[:, 1] +
                2000 -
                0.05 * (X[:, 2] - 25) ** 2 * 100
            )
            y = y / 10.0
            self.yield_model = RandomForestRegressor(n_estimators=120, random_state=42)
            self.yield_model.fit(X, y)

        if self.weather_model is None:
            # Demo weather: predict rainfall trend over years
            years = np.arange(2010, 2024)
            rainfall = 40 + 0.9 * (years - 2010) + np.sin((years - 2010) / 2) * 4
            rainfall = rainfall + np.random.default_rng(1).normal(0, 1.8, size=len(years))
            X = years.reshape(-1, 1)
            y = rainfall
            self.weather_model = LinearRegression()
            self.weather_model.fit(X, y)

    def predict_yield(self, rainfall: float, pesticide: float, temperature: float):
        self._ensure_models()
        X = np.array([[rainfall, pesticide, temperature]], dtype=float)
        pred = float(self.yield_model.predict(X)[0])
        return {
            "predicted_yield_kg_per_ha": round(pred, 2),
            "note": "Demo model prediction (replace with your pretrained RandomForest model for real results).",
        }

    def predict_disease(self, image_bytes=None, image_hint: str = "leaf"):
        # Demo: deterministic-ish based on hint length
        idx = (len(image_hint or "leaf") * 7) % len(self.disease_classes)
        disease = self.disease_classes[idx]
        return {
            "predicted_disease": disease,
            "confidence": round(0.55 + (idx % 10) * 0.04, 2),
            "recommendation": "Demo recommendation: consult local extension services and compare with your crop-specific symptoms. Replace CNN model for accurate diagnosis.",
        }

    def recommend_fertilizer(self, crop_type: str, soil_type: str, growth_stage: str, rainfall: float):
        # Simple rule-based NPK heuristic.
        crop_factor = {
            "wheat": 1.0,
            "rice": 1.2,
            "maize": 1.1,
            "tomato": 1.3,
            "potato": 1.25,
            "pepper": 1.15,
        }.get(crop_type.lower().strip(), 1.1)

        stage_factor = {
            "seedling": 0.8,
            "vegetative": 1.0,
            "flowering": 1.15,
            "fruiting": 1.25,
        }.get(growth_stage.lower().strip(), 1.0)

        soil_factor = {
            "sandy": (0.95, 1.0, 1.05),
            "loamy": (1.0, 1.0, 1.0),
            "clay": (1.05, 0.95, 0.95),
        }.get(soil_type.lower().strip(), (1.0, 1.0, 1.0))

        # rainfall affects N (more leaching -> reduce N)
        n_leach = max(0.0, (rainfall - 100) / 200)

        base_npk = np.array([120, 60, 80], dtype=float)
        multipliers = np.array([soil_factor[0], soil_factor[1], soil_factor[2]], dtype=float)
        npk = base_npk * crop_factor * stage_factor * multipliers
        npk[0] = npk[0] * (1 - 0.3 * n_leach)  # reduce N with higher rainfall

        n, p, k = npk
        return {
            "crop": crop_type,
            "soil": soil_type,
            "growth_stage": growth_stage,
            "recommended_N_kg_ha": round(float(n), 2),
            "recommended_P_kg_ha": round(float(p), 2),
            "recommended_K_kg_ha": round(float(k), 2),
            "note": "Rule-based demo recommendation. Replace with your trained fertilizer ML model for production-grade suggestions.",
        }

    def predict_weather(self, year: int):
        self._ensure_models()
        X = np.array([[year]], dtype=float)
        rainfall = float(self.weather_model.predict(X)[0])
        # Advisory
        advisory = "Plan irrigation based on predicted rainfall and local evapotranspiration; validate with nearby weather station readings."
        if rainfall < 45:
            advisory = "Predicted low rainfall. Increase monitoring, plan supplemental irrigation, and consider moisture-conserving mulching."
        elif rainfall > 65:
            advisory = "Predicted higher rainfall. Ensure proper drainage and adjust irrigation schedule to avoid waterlogging."

        return {
            "year": year,
            "predicted_rainfall_mm": round(rainfall, 2),
            "advisory": advisory,
            "note": "Demo linear regression forecast. Replace with your trained rainfall model for real results.",
        }


model_service = ModelService()

