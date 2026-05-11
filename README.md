# AgriSmart (Flask) — Local Host Run

This is a complete, runnable Flask project generated from the AgriSmart description. It includes:
- Crop yield prediction (RandomForestRegressor style; demo fallback)
- Disease detection (CNN placeholder; demo fallback)
- Fertilizer recommendation (rule-based + demo fallback)
- Weather prediction (LinearRegression style; demo fallback)

> Note: Since no real pretrained models/datasets are provided here, the system auto-generates small demo models on first run and continues to work. You can later replace the demo model files with your own pretrained models.

## Prerequisites
- Python 3.10+ recommended

## Setup (Windows)
From the project folder:

```bat
cd "c:/Users/priya/OneDrive/Documents/Desktop/CLI APP/agrismart"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open:
- http://127.0.0.1:5000

## REST API
- `POST /api/predict-yield`
- `POST /api/predict-disease`
- `POST /api/recommend-fertilizer`
- `POST /api/predict-weather`

Each endpoint accepts JSON.

## How to replace models later
- Place model files under `models/` (see `ml/model_loader.py` for expected names).
- If a model file is missing, the app uses a demo model so the UI still works.

