import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    # Flask Secret Key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "cloudsentinel-marketlink-secret-2026"
    )

    # SQLite Database
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(BASE_DIR, "instance", "marketlink.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload Settings
    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads",
        "listings"
    )

    ALLOWED_IMAGE_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png"
    }

    # Maximum Image Size = 1MB
    MAX_IMAGE_SIZE = 1 * 1024 * 1024
