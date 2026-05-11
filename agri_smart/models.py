"""
AgriSmart – ML model wrappers
All models fall back to deterministic demo logic when no saved model file
is present, so the app runs out-of-the-box without a GPU or dataset.
"""

import os
import io
import random
import math
import logging

import numpy as np
import joblib

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _load_joblib(filename):
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        try:
            return joblib.load(path)
        except Exception as exc:
            logger.warning("Could not load %s: %s", filename, exc)
    return None


# ──────────────────────────────────────────────
# 1. Crop Yield Prediction
# ──────────────────────────────────────────────

_yield_model   = _load_joblib("yield_model.pkl")
_yield_scaler  = _load_joblib("yield_scaler.pkl")

# Realistic per-crop base yields (tonnes/ha)
_CROP_YIELD_BASE = {
    "maize": 5.2, "potatoes": 18.4, "rice, paddy": 4.6,
    "sorghum": 1.8, "soybeans": 2.5, "wheat": 3.4,
    "cassava": 11.2, "sweet potatoes": 9.8, "yams": 8.5,
    "plantains and others": 6.3,
}

def predict_yield(crop: str, rainfall_mm: float, pesticides_tonnes: float,
                  avg_temp_c: float) -> dict:
    """Return predicted yield and confidence band."""
    crop_key = crop.lower().strip()

    if _yield_model is not None:
        try:
            features = np.array([[rainfall_mm, pesticides_tonnes, avg_temp_c]])
            if _yield_scaler:
                features = _yield_scaler.transform(features)
            pred = float(_yield_model.predict(features)[0])
            return {"yield_tonnes_per_ha": round(pred, 2),
                    "low": round(pred * 0.88, 2),
                    "high": round(pred * 1.12, 2),
                    "model": "random_forest"}
        except Exception as exc:
            logger.warning("Yield model inference error: %s", exc)

    # ── Demo fallback ──
    base = _CROP_YIELD_BASE.get(crop_key, 4.0)
    rain_factor  = 1 + 0.0008 * (rainfall_mm - 800)
    temp_factor  = 1 - 0.012 * abs(avg_temp_c - 22)
    pest_factor  = 1 + 0.0003 * min(pesticides_tonnes, 500)
    pred = max(0.5, base * rain_factor * temp_factor * pest_factor)
    return {
        "yield_tonnes_per_ha": round(pred, 2),
        "low":  round(pred * 0.88, 2),
        "high": round(pred * 1.12, 2),
        "model": "demo_formula",
    }


# ──────────────────────────────────────────────
# 2. Plant Disease Detection
# ──────────────────────────────────────────────

DISEASE_CLASSES = [
    "Apple – Apple scab",
    "Apple – Black rot",
    "Apple – Cedar apple rust",
    "Apple – Healthy",
    "Cherry – Powdery mildew",
    "Cherry – Healthy",
    "Corn – Gray leaf spot",
    "Corn – Common rust",
    "Corn – Northern leaf blight",
    "Corn – Healthy",
    "Grape – Black rot",
    "Grape – Esca (Black measles)",
    "Grape – Leaf blight",
    "Grape – Healthy",
    "Orange – Citrus greening (HLB)",
    "Peach – Bacterial spot",
    "Peach – Healthy",
    "Pepper – Bacterial spot",
    "Pepper – Healthy",
    "Potato – Early blight",
    "Potato – Late blight",
    "Potato – Healthy",
    "Raspberry – Healthy",
    "Soybean – Healthy",
    "Squash – Powdery mildew",
    "Strawberry – Leaf scorch",
    "Strawberry – Healthy",
    "Tomato – Bacterial spot",
    "Tomato – Early blight",
    "Tomato – Late blight",
    "Tomato – Leaf mold",
    "Tomato – Septoria leaf spot",
    "Tomato – Healthy",
]

DISEASE_TREATMENTS = {
    "Apple – Apple scab":         "Apply fungicides (captan/mancozeb) at bud break. Remove infected leaves.",
    "Apple – Black rot":          "Prune cankers, apply copper fungicides, remove mummified fruit.",
    "Apple – Cedar apple rust":   "Apply myclobutanil fungicide; remove nearby cedar trees if possible.",
    "Apple – Healthy":            "No treatment needed. Continue regular monitoring.",
    "Cherry – Powdery mildew":    "Apply sulfur-based fungicide; improve air circulation by pruning.",
    "Cherry – Healthy":           "No treatment needed.",
    "Corn – Gray leaf spot":      "Use resistant varieties; apply strobilurin fungicides at tasseling.",
    "Corn – Common rust":         "Apply fungicides (azoxystrobin); plant rust-resistant hybrids.",
    "Corn – Northern leaf blight":"Apply triazole fungicides at early disease onset; rotate crops.",
    "Corn – Healthy":             "No treatment needed.",
    "Grape – Black rot":          "Apply mancozeb or myclobutanil; remove infected berries promptly.",
    "Grape – Esca (Black measles)":"No cure; remove infected wood, avoid large pruning wounds.",
    "Grape – Leaf blight":        "Apply copper fungicides; ensure good canopy ventilation.",
    "Grape – Healthy":            "No treatment needed.",
    "Orange – Citrus greening (HLB)":"No cure; remove infected trees; control Asian citrus psyllid vector.",
    "Peach – Bacterial spot":     "Apply copper bactericides; plant resistant varieties.",
    "Peach – Healthy":            "No treatment needed.",
    "Pepper – Bacterial spot":    "Use copper-based bactericides; avoid overhead irrigation.",
    "Pepper – Healthy":           "No treatment needed.",
    "Potato – Early blight":      "Apply chlorothalonil or mancozeb; ensure adequate potassium nutrition.",
    "Potato – Late blight":       "Apply metalaxyl fungicides immediately; destroy infected foliage.",
    "Potato – Healthy":           "No treatment needed.",
    "Raspberry – Healthy":        "No treatment needed.",
    "Soybean – Healthy":          "No treatment needed.",
    "Squash – Powdery mildew":    "Apply potassium bicarbonate or sulfur fungicide; improve air flow.",
    "Strawberry – Leaf scorch":   "Remove infected leaves; apply captan fungicide.",
    "Strawberry – Healthy":       "No treatment needed.",
    "Tomato – Bacterial spot":    "Apply copper bactericides; use disease-free transplants.",
    "Tomato – Early blight":      "Apply chlorothalonil; remove lower infected leaves; mulch soil.",
    "Tomato – Late blight":       "Apply metalaxyl+mancozeb; destroy infected plants immediately.",
    "Tomato – Leaf mold":         "Improve ventilation; apply copper fungicide.",
    "Tomato – Septoria leaf spot":"Apply mancozeb; remove infected foliage; stake plants.",
    "Tomato – Healthy":           "No treatment needed.",
}

_disease_model = None

def _try_load_keras():
    global _disease_model
    model_path = os.path.join(MODELS_DIR, "disease_model.h5")
    if not os.path.exists(model_path):
        return
    try:
        from tensorflow import keras
        _disease_model = keras.models.load_model(model_path)
        logger.info("Keras disease model loaded.")
    except Exception as exc:
        logger.warning("Could not load Keras model: %s", exc)

_try_load_keras()


def predict_disease(image_bytes: bytes) -> dict:
    """Classify a leaf image. Falls back to demo heuristic."""
    if _disease_model is not None:
        try:
            from PIL import Image
            import tensorflow as tf
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
            arr = np.array(img, dtype="float32") / 255.0
            arr = np.expand_dims(arr, 0)
            preds = _disease_model.predict(arr)[0]
            idx   = int(np.argmax(preds))
            conf  = float(preds[idx])
            label = DISEASE_CLASSES[idx] if idx < len(DISEASE_CLASSES) else "Unknown"
            return {"disease": label,
                    "confidence": round(conf * 100, 1),
                    "treatment": DISEASE_TREATMENTS.get(label, "Consult an agronomist."),
                    "model": "cnn"}
        except Exception as exc:
            logger.warning("Disease model inference error: %s", exc)

    # ── Demo fallback: use image bytes as seed for reproducibility ──
    seed = sum(image_bytes[:64]) if image_bytes else 42
    rng  = random.Random(seed)
    idx  = rng.randint(0, len(DISEASE_CLASSES) - 1)
    conf = round(rng.uniform(78.0, 96.5), 1)
    label = DISEASE_CLASSES[idx]
    return {
        "disease":    label,
        "confidence": conf,
        "treatment":  DISEASE_TREATMENTS.get(label, "Consult an agronomist."),
        "model":      "demo",
    }


# ──────────────────────────────────────────────
# 3. Fertilizer Recommendation
# ──────────────────────────────────────────────

_fert_model = _load_joblib("fertilizer_model.pkl")

FERTILIZER_DB = {
    # (crop_group, soil_type): (N, P, K, product_name)
    ("cereal",    "loamy"):  (120, 60, 40, "NPK 20-10-7"),
    ("cereal",    "sandy"):  (140, 50, 35, "NPK 23-8-6"),
    ("cereal",    "clay"):   (100, 65, 45, "NPK 16-10-7"),
    ("legume",    "loamy"):  (20,  80, 60, "NPK 3-13-10"),
    ("legume",    "sandy"):  (25,  70, 55, "NPK 4-11-9"),
    ("legume",    "clay"):   (15,  90, 65, "NPK 2-15-11"),
    ("vegetable", "loamy"):  (150, 70, 80, "NPK 20-9-11"),
    ("vegetable", "sandy"):  (170, 60, 75, "NPK 22-8-10"),
    ("vegetable", "clay"):   (130, 75, 85, "NPK 17-10-11"),
    ("fruit",     "loamy"):  (100, 50, 100,"NPK 12-6-12"),
    ("fruit",     "sandy"):  (120, 45, 95, "NPK 15-6-12"),
    ("fruit",     "clay"):   (90,  55, 105,"NPK 11-7-13"),
}

CROP_GROUPS = {
    "rice": "cereal", "wheat": "cereal", "maize": "cereal",
    "sorghum": "cereal", "barley": "cereal", "oats": "cereal",
    "soybean": "legume", "groundnut": "legume", "chickpea": "legume",
    "lentil": "legume", "pea": "legume", "beans": "legume",
    "tomato": "vegetable", "potato": "vegetable", "onion": "vegetable",
    "pepper": "vegetable", "cabbage": "vegetable", "carrot": "vegetable",
    "mango": "fruit", "banana": "fruit", "apple": "fruit",
    "grape": "fruit", "orange": "fruit", "sugarcane": "fruit",
}


def recommend_fertilizer(crop: str, soil_type: str, growth_stage: str,
                          rainfall_mm: float) -> dict:
    crop_key  = crop.lower().strip()
    soil_key  = soil_type.lower().strip()
    group     = CROP_GROUPS.get(crop_key, "cereal")
    key       = (group, soil_key)
    n, p, k, product = FERTILIZER_DB.get(
        key, FERTILIZER_DB.get((group, "loamy"), (120, 60, 40, "NPK 20-10-7"))
    )

    # Adjust for growth stage
    stage_factors = {"seedling": 0.6, "vegetative": 1.0,
                     "flowering": 0.9, "fruiting": 0.8, "maturity": 0.4}
    factor = stage_factors.get(growth_stage.lower(), 1.0)
    n = round(n * factor)
    p = round(p * factor)
    k = round(k * factor)

    # Low rain → reduce slightly
    if rainfall_mm < 400:
        n = round(n * 0.85)

    notes = []
    if rainfall_mm < 300:
        notes.append("Low rainfall detected — consider drip irrigation alongside fertilizer application.")
    if growth_stage.lower() == "flowering":
        notes.append("Reduce nitrogen during flowering to prevent excessive vegetative growth.")
    if soil_key == "sandy":
        notes.append("Sandy soils have low retention — split fertilizer into 2–3 applications.")

    return {
        "crop": crop, "soil_type": soil_type,
        "growth_stage": growth_stage,
        "N_kg_per_ha": n, "P_kg_per_ha": p, "K_kg_per_ha": k,
        "recommended_product": product,
        "notes": notes if notes else ["Apply as a single basal dose before planting."],
    }


# ──────────────────────────────────────────────
# 4. Weather / Rainfall Prediction
# ──────────────────────────────────────────────

_weather_model  = _load_joblib("weather_model.pkl")

# Synthetic historical data (mm/year) to populate charts
_BASE_RAINFALL = {
    1990: 820, 1991: 795, 1992: 860, 1993: 910, 1994: 780,
    1995: 835, 1996: 870, 1997: 760, 1998: 990, 1999: 850,
    2000: 880, 2001: 820, 2002: 740, 2003: 800, 2004: 865,
    2005: 900, 2006: 840, 2007: 875, 2008: 920, 2009: 810,
    2010: 960, 2011: 895, 2012: 770, 2013: 830, 2014: 855,
    2015: 790, 2016: 875, 2017: 910, 2018: 840, 2019: 870,
    2020: 825, 2021: 890, 2022: 850, 2023: 870, 2024: 880,
}


def predict_weather(target_year: int) -> dict:
    years  = sorted(_BASE_RAINFALL.keys())
    values = [_BASE_RAINFALL[y] for y in years]

    if _weather_model is not None:
        try:
            pred = float(_weather_model.predict([[target_year]])[0])
        except Exception:
            pred = None
    else:
        pred = None

    if pred is None:
        # Linear regression fallback (manual)
        n   = len(years)
        x_m = sum(years) / n
        y_m = sum(values) / n
        b1  = sum((y - x_m) * (v - y_m) for y, v in zip(years, values)) / \
              sum((y - x_m) ** 2 for y in years)
        b0  = y_m - b1 * x_m
        pred = b0 + b1 * target_year

    pred = round(max(200, pred), 1)

    advisory = []
    if pred < 600:
        advisory = ["Severe drought risk — invest in irrigation infrastructure.",
                    "Plant drought-tolerant varieties (millets, sorghum).",
                    "Harvest rainwater during any rainfall events."]
    elif pred < 800:
        advisory = ["Below-average rainfall expected — conserve soil moisture.",
                    "Use mulching to reduce evaporation.",
                    "Schedule irrigation to supplement deficit."]
    elif pred < 1000:
        advisory = ["Near-normal rainfall — standard crop calendar applies.",
                    "Monitor soil moisture and irrigate during dry spells.",
                    "Good conditions for most Kharif and Rabi crops."]
    else:
        advisory = ["Above-average rainfall — watch for waterlogging.",
                    "Ensure proper field drainage before planting.",
                    "Risk of fungal diseases increases; monitor crops closely."]

    return {
        "target_year":        target_year,
        "predicted_rainfall": pred,
        "historical_years":   years,
        "historical_values":  values,
        "advisory":           advisory,
    }
