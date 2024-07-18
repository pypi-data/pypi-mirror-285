""" Flask configuration """

import os


class Config(object):
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", default=False)
    ID = os.environ.get("ID", default=None)
    DEFAULT_PORT = "5000"
    CORS_HEADERS = "Content-Type"
    UPLOAD_FOLDER = "./uploads"
    WORKFLOWS_DATA_FOLDER = "./data_workflows/"
    LOCK_FOLDER = "./lock/"
    TIME_FOLDER = "./time/"


class ProdConfig(Config):
    SSL = None
    ORIGINS = ["https://geode-solutions.com", "https://next.geode-solutions.com"]
    MINUTES_BEFORE_TIMEOUT = "5"
    SECONDS_BETWEEN_SHUTDOWNS = "150"
    DEFAULT_DATA_FOLDER_PATH = "/data/"


class DevConfig(Config):
    SSL = None
    ORIGINS = "http://localhost:3000"
    MINUTES_BEFORE_TIMEOUT = "1000"
    SECONDS_BETWEEN_SHUTDOWNS = "60"
    DEFAULT_DATA_FOLDER_PATH = "./data/"
