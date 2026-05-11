"""
AgriSmart – Flask route definitions
Web UI routes + REST API endpoints
"""

import io
import traceback
import logging

from flask import (Blueprint, render_template, request,
                   jsonify, redirect, url_for, flash)

from .models import (
    predict_yield,
    predict_disease,
    recommend_fertilizer,
    predict_weather,
    DISEASE_CLASSES,
    _BASE_RAINFALL,
)

logger  = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)

CROP_LIST = [
    "Maize", "Potatoes", "Rice, paddy", "Sorghum", "Soybeans",
    "Wheat", "Cassava", "Sweet potatoes", "Yams", "Plantains and others",
]

FERT_CROPS = [
    "Rice", "Wheat", "Maize", "Sorghum", "Barley",
    "Soybean", "Groundnut", "Chickpea", "Lentil", "Pea", "Beans",
    "Tomato", "Potato", "Onion", "Pepper", "Cabbage", "Carrot",
    "Mango", "Banana", "Apple", "Grape", "Orange", "Sugarcane",
]

SOIL_TYPES    = ["Loamy", "Sandy", "Clay", "Silty", "Peaty", "Chalky"]
GROWTH_STAGES = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Maturity"]

# ─────────────────────────── Web Pages ────────────────────────────

@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/yield-prediction", methods=["GET", "POST"])
def yield_prediction():
    result = None
    error  = None
    form   = {}

    if request.method == "POST":
        try:
            form = request.form
            crop       = form.get("crop", "Wheat")
            rainfall   = float(form.get("rainfall", 800))
            pesticides = float(form.get("pesticides", 50))
            avg_temp   = float(form.get("avg_temp", 22))

            result = predict_yield(crop, rainfall, pesticides, avg_temp)
            result["crop"] = crop
        except Exception:
            error = "Invalid input — please check your values and try again."
            logger.error(traceback.format_exc())

    return render_template(
        "yield_prediction.html",
        crop_list=CROP_LIST, result=result, error=error, form=form
    )


@main_bp.route("/disease-prediction", methods=["GET", "POST"])
def disease_prediction():
    result = None
    error  = None

    if request.method == "POST":
        try:
            file = request.files.get("leaf_image")
            if not file or file.filename == "":
                error = "Please upload a leaf image."
            else:
                image_bytes = file.read()
                result = predict_disease(image_bytes)
        except Exception:
            error = "Could not process image — please try a different file."
            logger.error(traceback.format_exc())

    return render_template(
        "disease_prediction.html",
        result=result, error=error,
        total_classes=len(DISEASE_CLASSES)
    )


@main_bp.route("/fertilizer-recommendation", methods=["GET", "POST"])
def fertilizer_recommendation():
    result = None
    error  = None
    form   = {}

    if request.method == "POST":
        try:
            form = request.form
            crop     = form.get("crop", "Wheat")
            soil     = form.get("soil_type", "Loamy")
            stage    = form.get("growth_stage", "Vegetative")
            rainfall = float(form.get("rainfall", 600))

            result = recommend_fertilizer(crop, soil, stage, rainfall)
        except Exception:
            error = "Invalid input — please check your values and try again."
            logger.error(traceback.format_exc())

    return render_template(
        "fertilizer_recommendation.html",
        crop_list=FERT_CROPS,
        soil_types=SOIL_TYPES,
        growth_stages=GROWTH_STAGES,
        result=result, error=error, form=form
    )


@main_bp.route("/weather-prediction", methods=["GET", "POST"])
def weather_prediction():
    result      = None
    error       = None
    target_year = None

    if request.method == "POST":
        try:
            target_year = int(request.form.get("target_year", 2025))
            if target_year < 1980 or target_year > 2100:
                error = "Please enter a year between 1980 and 2100."
            else:
                result = predict_weather(target_year)
        except Exception:
            error = "Invalid year — please enter a valid 4-digit year."
            logger.error(traceback.format_exc())

    # Always pass historical data for the chart
    hist_years  = sorted(_BASE_RAINFALL.keys())
    hist_values = [_BASE_RAINFALL[y] for y in hist_years]

    return render_template(
        "weather_prediction.html",
        result=result, error=error,
        target_year=target_year,
        hist_years=hist_years,
        hist_values=hist_values,
    )


@main_bp.route("/about")
def about():
    return render_template("about.html")


# ─────────────────────────── REST API ────────────────────────────

@main_bp.route("/api/predict-yield", methods=["POST"])
def api_predict_yield():
    try:
        data = request.get_json(force=True) or {}
        crop       = data.get("crop", "Wheat")
        rainfall   = float(data.get("rainfall_mm", 800))
        pesticides = float(data.get("pesticides_tonnes", 50))
        avg_temp   = float(data.get("avg_temp_c", 22))
        result = predict_yield(crop, rainfall, pesticides, avg_temp)
        result["crop"] = crop
        return jsonify({"success": True, "data": result})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@main_bp.route("/api/predict-disease", methods=["POST"])
def api_predict_disease():
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"success": False, "error": "No image uploaded"}), 400
        result = predict_disease(file.read())
        return jsonify({"success": True, "data": result})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@main_bp.route("/api/recommend-fertilizer", methods=["POST"])
def api_recommend_fertilizer():
    try:
        data  = request.get_json(force=True) or {}
        crop  = data.get("crop", "Wheat")
        soil  = data.get("soil_type", "Loamy")
        stage = data.get("growth_stage", "Vegetative")
        rain  = float(data.get("rainfall_mm", 600))
        result = recommend_fertilizer(crop, soil, stage, rain)
        return jsonify({"success": True, "data": result})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@main_bp.route("/api/predict-weather", methods=["POST"])
def api_predict_weather():
    try:
        data = request.get_json(force=True) or {}
        year = int(data.get("year", 2025))
        result = predict_weather(year)
        return jsonify({"success": True, "data": result})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


# ─────────────────────────── Error handlers ────────────────────────────

@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template("404.html", code=500,
                           message="Internal Server Error"), 500
