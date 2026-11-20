"""Conexión a MongoDB Atlas. Las credenciales vienen del archivo .env (nunca en el código)."""
import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "musica_recomendador")

# Qué variable del .env usa cada rol (si falta la primera, intenta la siguiente)
ORDEN = {
    "admin": ["MONGO_URI"],
    "app": ["MONGO_URI_APP", "MONGO_URI"],
    "lectura": ["MONGO_URI_LECTURA", "MONGO_URI_APP", "MONGO_URI"],
}


@lru_cache(maxsize=None)
def _cliente(uri):
    return MongoClient(uri, serverSelectionTimeoutMS=8000)


def db_desde_variable(nombre):
    """Devuelve la base usando la variable del .env indicada, o None si no existe."""
    uri = os.getenv(nombre)
    return _cliente(uri)[DB_NAME] if uri else None


def get_db(rol="app"):
    for nombre in ORDEN[rol]:
        db = db_desde_variable(nombre)
        if db is not None:
            return db
    raise RuntimeError(f"Falta configurar {ORDEN[rol][0]} en el archivo .env")
