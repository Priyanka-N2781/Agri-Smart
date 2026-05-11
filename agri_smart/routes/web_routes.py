import io
from flask import Blueprint, render_template, request

from agri_smart.ml.model_loader import model_service

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def home():
    return render_template("index.html")


@web_bp.get("/yield-prediction")
def yield_page():
    return render_template("yield_prediction.html")


@web_bp.post("/yield-prediction")
def yield_predict():
    rainfall = float(request.form["rainfall"])
    pesticide = float(request.form["pesticide"])
    temperature = float(request.form["temperature"])
    result = model_service.predict_yield(rainfall=rainfall, pesticide=pesticide, temperature=temperature)
    return render_template("yield_prediction.html", prediction=result)


@web_bp.get("/disease-prediction")
def disease_page():
    return render_template("disease_prediction.html")


@web_bp.post("/disease-prediction")
def disease_predict():

    # Accept uploaded image
    file = request.files.get("leaf_image")
    if not file:
        return render_template("disease_prediction.html", error="No image uploaded")
    image_bytes = file.read()
    result = model_service.predict_disease(image_bytes=image_bytes)
    return render_template("disease_prediction.html", prediction=result)


@web_bp.get("/fertilizer-recommendation")
def fertilizer_page():
    return render_template("fertilizer_recommendation.html")


@web_bp.post("/fertilizer-recommendation")
def fertilizer_recommend():
    crop_type = request.form["crop_type"]
    soil_type = request.form["soil_type"]
    growth_stage = request.form["growth_stage"]
    rainfall = float(request.form["rainfall"])
    result = model_service.recommend_fertilizer(crop_type=crop_type, soil_type=soil_type, growth_stage=growth_stage, rainfall=rainfall)
    return render_template("fertilizer_recommendation.html", prediction=result)


@web_bp.get("/weather-prediction")
def weather_page():
    return render_template("weather_prediction.html")


@web_bp.post("/weather-prediction")
def weather_predict():
    year = int(request.form["year"])
    result = model_service.predict_weather(year=year)
    return render_template("weather_prediction.html", prediction=result)


@web_bp.get("/about")
def about_page():
    return render_template("about.html")

