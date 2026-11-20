"""Paso 4: CRUD completo contra Atlas (Create, Read, Update, Delete) con el usuario de la app."""
import _ruta  # noqa: F401
from app.config import get_db

db = get_db("app")
col = db.canciones

print("CREATE")
nuevo_id = col.find_one(sort=[("_id", -1)])["_id"] + 1
col.insert_one({"_id": nuevo_id, "titulo": "Canción de prueba", "artista_id": 1,
                "artista": "Demo", "genero": "Rock", "duracion_seg": 200, "anio": 2024})
print("  insertada con _id", nuevo_id)

print("READ")
print("  ", col.find_one({"_id": nuevo_id}))
print("   Rock desde 2010:", col.count_documents({"genero": "Rock", "anio": {"$gte": 2010}}))

print("UPDATE")
col.update_one({"_id": nuevo_id}, {"$set": {"anio": 2025, "titulo": "Canción editada"}})
print("  ", col.find_one({"_id": nuevo_id}))

print("DELETE")
print("   eliminadas:", col.delete_one({"_id": nuevo_id}).deleted_count)
