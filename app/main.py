"""API REST del recomendador. Se conecta a MongoDB Atlas y expone los datos (consumo de datos)."""
import re
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pymongo.errors import OperationFailure, PyMongoError, WriteError

from . import consultas
from .config import get_db

app = FastAPI(title="Recomendador de música", version="1.0")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def bd():
    """Base de datos con el usuario de la aplicación (rol readWrite)."""
    return get_db("app")


# ---------------- Manejo de errores (seguridad / validación) ----------------
@app.exception_handler(OperationFailure)
async def error_operacion(request, exc):
    if exc.code == 13:  # Unauthorized
        return JSONResponse(status_code=403, content={
            "detalle": "El usuario de base de datos no tiene permiso para esta operación."})
    if exc.code == 121:  # Document failed validation
        return JSONResponse(status_code=422, content={
            "detalle": "Documento rechazado por la validación de esquema de MongoDB."})
    return JSONResponse(status_code=500, content={"detalle": str(exc)})


@app.exception_handler(PyMongoError)
async def error_mongo(request, exc):
    return JSONResponse(status_code=503, content={
        "detalle": "No se pudo conectar con MongoDB Atlas. Revisa .env y Network Access."})


@app.exception_handler(RuntimeError)
async def error_config(request, exc):
    return JSONResponse(status_code=500, content={"detalle": str(exc)})


# ---------------- Modelos de entrada ----------------
class CancionIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=120)
    artista_id: int
    genero: str = Field(min_length=1, max_length=40)
    duracion_seg: int = Field(ge=30, le=3600)
    anio: int = Field(ge=1600, le=2100)


class ReproduccionIn(BaseModel):
    usuario_id: int
    cancion_id: int
    calificacion: int = Field(ge=1, le=5)


# ---------------- Páginas y estado ----------------
@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(STATIC / "index.html")


@app.get("/api/salud")
def salud():
    db = bd()
    db.client.admin.command("ping")
    return {"estado": "conectado", "base": db.name,
            "documentos": {c: db[c].estimated_document_count()
                           for c in ["usuarios", "artistas", "canciones", "reproducciones"]}}


@app.get("/api/generos")
def generos():
    return sorted(bd().canciones.distinct("genero"))


# ---------------- CRUD de canciones ----------------
@app.get("/api/canciones")
def listar_canciones(q: str = "", genero: str = "", anio_min: int = 0,
                     limite: int = Query(20, ge=1, le=100), saltar: int = Query(0, ge=0)):
    filtro = {}
    if q:
        filtro["titulo"] = {"$regex": re.escape(q), "$options": "i"}
    if genero:
        filtro["genero"] = genero
    if anio_min:
        filtro["anio"] = {"$gte": anio_min}
    col = bd().canciones
    return {"total": col.count_documents(filtro),
            "items": list(col.find(filtro).sort("_id", 1).skip(saltar).limit(limite))}


@app.get("/api/canciones/{cancion_id}")
def obtener_cancion(cancion_id: int):
    c = bd().canciones.find_one({"_id": cancion_id})
    if not c:
        raise HTTPException(404, "La canción no existe")
    return c


@app.post("/api/canciones", status_code=201)
def crear_cancion(c: CancionIn):
    db = bd()
    artista = db.artistas.find_one({"_id": c.artista_id})
    if not artista:
        raise HTTPException(404, "El artista no existe")
    ultimo = db.canciones.find_one(sort=[("_id", -1)])
    doc = {"_id": (ultimo["_id"] if ultimo else 0) + 1,
           **c.model_dump(), "artista": artista["nombre"]}
    db.canciones.insert_one(doc)
    return doc


@app.put("/api/canciones/{cancion_id}")
def actualizar_cancion(cancion_id: int, c: CancionIn):
    db = bd()
    artista = db.artistas.find_one({"_id": c.artista_id})
    if not artista:
        raise HTTPException(404, "El artista no existe")
    r = db.canciones.update_one({"_id": cancion_id},
                                {"$set": {**c.model_dump(), "artista": artista["nombre"]}})
    if r.matched_count == 0:
        raise HTTPException(404, "La canción no existe")
    return db.canciones.find_one({"_id": cancion_id})


@app.delete("/api/canciones/{cancion_id}")
def borrar_cancion(cancion_id: int):
    db = bd()
    r = db.canciones.delete_one({"_id": cancion_id})
    if r.deleted_count == 0:
        raise HTTPException(404, "La canción no existe")
    borradas = db.reproducciones.delete_many({"cancion_id": cancion_id}).deleted_count
    return {"eliminada": cancion_id, "reproducciones_eliminadas": borradas}


# ---------------- Reproducciones y usuarios ----------------
@app.post("/api/reproducciones", status_code=201)
def registrar_reproduccion(r: ReproduccionIn):
    db = bd()
    cancion = db.canciones.find_one({"_id": r.cancion_id})
    if not cancion:
        raise HTTPException(404, "La canción no existe")
    if not db.usuarios.find_one({"_id": r.usuario_id}, {"_id": 1}):
        raise HTTPException(404, "El usuario no existe")
    doc = {**r.model_dump(), "artista_id": cancion["artista_id"],
           "genero": cancion["genero"], "fecha": datetime.now()}
    db.reproducciones.insert_one(doc)
    doc.pop("_id", None)
    return doc


@app.get("/api/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    u = bd().usuarios.find_one({"_id": usuario_id})
    if not u:
        raise HTTPException(404, "El usuario no existe")
    return u


# ---------------- Recomendaciones y estadísticas ----------------
@app.get("/api/top-canciones")
def top(limite: int = Query(10, ge=1, le=50)):
    return consultas.top_canciones(bd(), limite)


@app.get("/api/recomendaciones/{usuario_id}")
def recomendar(usuario_id: int, limite: int = Query(10, ge=1, le=50)):
    return consultas.recomendaciones(bd(), usuario_id, limite)


@app.get("/api/tambien-escucharon/{cancion_id}")
def tambien(cancion_id: int, limite: int = Query(10, ge=1, le=50)):
    return consultas.tambien_escucharon(bd(), cancion_id, limite)


@app.get("/api/artistas-relacionados/{artista_id}")
def relacionados(artista_id: int, limite: int = Query(5, ge=1, le=20)):
    return consultas.artistas_relacionados(bd(), artista_id, limite)


@app.get("/api/genero-por-ciudad")
def genero_ciudad():
    return consultas.genero_por_ciudad(bd())


# ---------------- Demostración de validación de esquema ----------------
@app.post("/api/demo-validacion")
def demo_validacion():
    """Intenta insertar documentos inválidos: MongoDB debe rechazarlos."""
    db = bd()
    pruebas = [
        ("Canción con año 1500 (mínimo 1900)", db.canciones,
         {"_id": 9999991, "titulo": "Prueba", "artista_id": 1, "genero": "Rock",
          "duracion_seg": 200, "anio": 1500}),
        ("Canción sin título (campo obligatorio)", db.canciones,
         {"_id": 9999992, "artista_id": 1, "genero": "Rock", "duracion_seg": 200, "anio": 2024}),
        ("Reproducción con calificación 9 (máximo 5)", db.reproducciones,
         {"usuario_id": 1, "cancion_id": 1, "calificacion": 9, "fecha": datetime.now()}),
    ]
    resultado = []
    for nombre, col, doc in pruebas:
        try:
            r = col.insert_one(doc)
            col.delete_one({"_id": r.inserted_id})
            resultado.append({"prueba": nombre, "rechazado": False, "codigo": None})
        except WriteError as e:
            resultado.append({"prueba": nombre, "rechazado": True, "codigo": e.code})
    return {"pruebas": resultado}