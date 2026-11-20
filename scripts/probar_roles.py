"""
Paso 2 (administración): prueba qué puede hacer cada usuario de base de datos.
Esperado:
  admin     -> lee, escribe y ve otras bases (admin, local)
  app       -> lee y escribe SOLO en musica_recomendador
  lectura   -> solo lee (la escritura debe ser rechazada)
"""
import _ruta  # noqa: F401
from pymongo.errors import PyMongoError

from app.config import db_desde_variable

ROLES = [("administrador", "MONGO_URI"),
         ("aplicación (readWrite)", "MONGO_URI_APP"),
         ("solo lectura (read)", "MONGO_URI_LECTURA")]


def probar(nombre, fn):
    try:
        return "PERMITIDO ", fn()
    except PyMongoError as e:
        return "RECHAZADO ", f"código {getattr(e, 'code', '?')}"


def escribir(db):
    db["_prueba_permisos"].insert_one({"x": 1})
    db["_prueba_permisos"].delete_many({})
    return "ok"


for etiqueta, variable in ROLES:
    db = db_desde_variable(variable)
    print(f"\n=== {etiqueta}  [{variable}] ===")
    if db is None:
        print("  (variable no configurada en .env, se omite)")
        continue
    for accion, fn in [
        ("leer canciones", lambda: db.canciones.count_documents({})),
        ("escribir documentos", lambda: escribir(db)),
        ("ver otras bases de datos", lambda: db.client.list_database_names()),
    ]:
        estado, detalle = probar(accion, fn)
        print(f"  {accion:28} {estado} {detalle}")
