from flask import Blueprint, jsonify, request

from agri_smart.ml.model_loader import model_service

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.post("/predict-yield")
def api_predict_yield():
    data = request.get_json(force=True)
    rainfall = float(data["rainfall"])
    pesticide = float(data["pesticide"])
    temperature = float(data["temperature"])
    pred = model_service.predict_yield(rainfall=rainfall, pesticide=pesticide, temperature=temperature)
    return jsonify(pred)


@api_bp.post("/predict-disease")
def api_predict_disease():
    data = request.get_json(force=True)
    # Expect base64 string or raw bytes not handled here; for demo we accept a filename-less dummy.
    # To keep it working without extra deps, we expect an optional "image_hint".
    hint = data.get("image_hint", "leaf")
    pred = model_service.predict_disease(image_bytes=None, image_hint=hint)
    return jsonify(pred)


@api_bp.post("/recommend-fertilizer")
def api_recommend_fertilizer():
    data = request.get_json(force=True)
    pred = model_service.recommend_fertilizer(
        crop_type=data["crop_type"],
        soil_type=data["soil_type"],
        growth_stage=data["growth_stage"],
        rainfall=float(data["rainfall"]),
    )
    return jsonify(pred)


@api_bp.post("/predict-weather")
def api_predict_weather():
    data = request.get_json(force=True)
    year = int(data["year"])
    pred = model_service.predict_weather(year=year)
    return jsonify(pred)

