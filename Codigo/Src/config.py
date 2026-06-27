import os


class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:18000/")
    MONGO_DB = os.getenv("MONGO_DB", "finis_trabaja")
    EMPRESA_DEMO_ID = os.getenv("EMPRESA_DEMO_ID", "empresa_demo_001")
    ESTUDIANTE_DEMO_ID = os.getenv("ESTUDIANTE_DEMO_ID", "estudiante_demo_001")
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024
    JSON_SORT_KEYS = False
