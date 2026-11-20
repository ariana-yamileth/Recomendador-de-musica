"""Paso 4: demuestra que la validación de esquema rechaza datos incorrectos."""
from datetime import datetime

import _ruta  # noqa: F401
from pymongo.errors import WriteError

from app.config import get_db

db = get_db("admin")

print("Validadores activos:")
for c in db.list_collections():
    if c.get("options", {}).get("validator"):
        print("  -", c["name"])

print("\nPrueba 1: calificación = 9 (fuera de 1 a 5) -> debe FALLAR")
try:
    db.reproducciones.insert_one({"usuario_id": 1, "cancion_id": 1,
                                  "calificacion": 9, "fecha": datetime.now()})
    print("  ERROR: se insertó (no debería)")
except WriteError as e:
    print("  Rechazado correctamente (código", e.code, ")")

print("\nPrueba 2: reproducción sin fecha -> debe FALLAR")
try:
    db.reproducciones.insert_one({"usuario_id": 1, "cancion_id": 1, "calificacion": 4})
    print("  ERROR: se insertó (no debería)")
except WriteError as e:
    print("  Rechazado correctamente (código", e.code, ")")
