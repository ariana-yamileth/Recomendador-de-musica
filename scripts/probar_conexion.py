"""Paso 1: comprueba la conexión a MongoDB Atlas."""
import _ruta  # noqa: F401
from app.config import get_db

db = get_db("admin")
db.client.admin.command("ping")
print("Conexión exitosa a MongoDB Atlas")
print("Base de datos:", db.name)
print("Colecciones:", db.list_collection_names() or "(aún no hay; ejecuta generar_datos.py)")
