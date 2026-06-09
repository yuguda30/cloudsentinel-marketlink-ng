import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    if os.environ.get("RENDER"):
        db_path = "/tmp/marketlink.db"
    else:
        db_path = os.path.join(basedir, "marketlink.db")

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "listings")

    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}

    MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 1MB only

database_url = os.environ.get("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = database_url or "sqlite:///" + os.path.join(BASE_DIR, "instance", "marketlink.db")