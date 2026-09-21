import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/finance-calculator-pgdatabase",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3001").split(",")
        if origin.strip()
    ]
    TEMPLATE_FILE = Path(
        os.getenv(
            "TEMPLATE_FILE",
            PROJECT_ROOT / "下载模板(Download template)" / "input_Data.xlsx",
        )
    )
    HOLDINGS_FILE = Path(
        os.getenv(
            "HOLDINGS_FILE",
            PROJECT_ROOT
            / "存放数据文件夹(The data to be collected)"
            / "holdings.xlsx",
        )
    )
    RUN_SCHEDULER = os.getenv("RUN_SCHEDULER", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE = Path(os.getenv("LOG_FILE", PROJECT_ROOT / "finance-calculator-flask" / "flask_error.log"))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RUN_SCHEDULER = False
