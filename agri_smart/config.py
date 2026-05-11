import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "agrismart-secret-2024")
    DEBUG = False
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

class DevelopmentConfig(Config):
    DEBUG = True

config = DevelopmentConfig()
