"""Validación de esquema ($jsonSchema): MongoDB rechaza documentos que no cumplan las reglas."""

VALIDADORES = {
    "usuarios": {"$jsonSchema": {
        "bsonType": "object",
        "required": ["nombre", "correo", "edad", "ciudad"],
        "properties": {
            "nombre": {"bsonType": "string"},
            "correo": {"bsonType": "string"},
            "edad": {"bsonType": "int", "minimum": 10, "maximum": 120},
            "ciudad": {"bsonType": "string"},
            "generos_favoritos": {"bsonType": "array"},
        }}},
    "canciones": {"$jsonSchema": {
        "bsonType": "object",
        "required": ["titulo", "artista_id", "genero", "anio"],
        "properties": {
            "titulo": {"bsonType": "string"},
            "genero": {"bsonType": "string"},
            "duracion_seg": {"bsonType": "int", "minimum": 30},
            "anio": {"bsonType": "int", "minimum": 1600, "maximum": 2100},
        }}},
    "reproducciones": {"$jsonSchema": {
        "bsonType": "object",
        "required": ["usuario_id", "cancion_id", "calificacion", "fecha"],
        "properties": {
            "usuario_id": {"bsonType": ["int", "long"]},
            "cancion_id": {"bsonType": ["int", "long"]},
            "calificacion": {"bsonType": "int", "minimum": 1, "maximum": 5,
                             "description": "entero entre 1 y 5"},
            "fecha": {"bsonType": "date"},
        }}},
}