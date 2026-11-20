"""Consultas del recomendador (aggregation pipelines). Cada función recibe la base `db`."""


def _datos_cancion():
    return [
        {"$lookup": {"from": "canciones", "localField": "_id",
                     "foreignField": "_id", "as": "c"}},
        {"$unwind": "$c"},
    ]


def tambien_escucharon(db, cancion_id, limite=10):
    """Quien escuchó la canción X también escuchó..."""
    oyentes = db.reproducciones.distinct("usuario_id", {"cancion_id": cancion_id})
    if not oyentes:
        return []
    pipeline = [
        {"$match": {"usuario_id": {"$in": oyentes}, "cancion_id": {"$ne": cancion_id}}},
        {"$group": {"_id": "$cancion_id", "oyentes": {"$addToSet": "$usuario_id"}}},
        {"$project": {"total": {"$size": "$oyentes"}}},
        {"$sort": {"total": -1, "_id": 1}},
        {"$limit": limite},
        *_datos_cancion(),
        {"$project": {"_id": 0, "cancion_id": "$_id", "titulo": "$c.titulo",
                      "artista": "$c.artista", "genero": "$c.genero", "total": 1}},
    ]
    return list(db.reproducciones.aggregate(pipeline))


def recomendaciones(db, usuario_id, limite=10):
    """Filtrado colaborativo: canciones que escuchan usuarios parecidos a mí y yo aún no."""
    mis = db.reproducciones.distinct("cancion_id", {"usuario_id": usuario_id})
    if not mis:
        return []
    pipeline = [
        {"$match": {"cancion_id": {"$in": mis}, "usuario_id": {"$ne": usuario_id}}},
        {"$group": {"_id": "$usuario_id", "en_comun": {"$sum": 1}}},
        {"$sort": {"en_comun": -1, "_id": 1}},
        {"$limit": 50},
        {"$lookup": {"from": "reproducciones", "localField": "_id",
                     "foreignField": "usuario_id", "as": "r"}},
        {"$unwind": "$r"},
        {"$match": {"r.cancion_id": {"$nin": mis}}},
        {"$group": {"_id": "$r.cancion_id", "puntaje": {"$sum": "$en_comun"}}},
        {"$sort": {"puntaje": -1, "_id": 1}},
        {"$limit": limite},
        *_datos_cancion(),
        {"$project": {"_id": 0, "cancion_id": "$_id", "titulo": "$c.titulo",
                      "artista": "$c.artista", "genero": "$c.genero", "puntaje": 1}},
    ]
    return list(db.reproducciones.aggregate(pipeline))


def artistas_relacionados(db, artista_id, limite=5):
    fans = db.reproducciones.distinct("usuario_id", {"artista_id": artista_id})
    if not fans:
        return []
    pipeline = [
        {"$match": {"usuario_id": {"$in": fans}, "artista_id": {"$ne": artista_id}}},
        {"$group": {"_id": "$artista_id", "fans": {"$addToSet": "$usuario_id"}}},
        {"$project": {"total": {"$size": "$fans"}}},
        {"$sort": {"total": -1, "_id": 1}},
        {"$limit": limite},
        {"$lookup": {"from": "artistas", "localField": "_id",
                     "foreignField": "_id", "as": "a"}},
        {"$unwind": "$a"},
        {"$project": {"_id": 0, "artista_id": "$_id", "artista": "$a.nombre", "total": 1}},
    ]
    return list(db.reproducciones.aggregate(pipeline))


def top_canciones(db, limite=10):
    pipeline = [
        {"$group": {"_id": "$cancion_id", "reproducciones": {"$sum": 1},
                    "promedio": {"$avg": "$calificacion"}}},
        {"$sort": {"reproducciones": -1, "_id": 1}},
        {"$limit": limite},
        *_datos_cancion(),
        {"$project": {"_id": 0, "cancion_id": "$_id", "titulo": "$c.titulo",
                      "artista": "$c.artista", "reproducciones": 1,
                      "promedio": {"$round": ["$promedio", 2]}}},
    ]
    return list(db.reproducciones.aggregate(pipeline))


def genero_por_ciudad(db):
    pipeline = [
        {"$lookup": {"from": "usuarios", "localField": "usuario_id",
                     "foreignField": "_id", "as": "u"}},
        {"$unwind": "$u"},
        {"$group": {"_id": {"ciudad": "$u.ciudad", "genero": "$genero"},
                    "total": {"$sum": 1}}},
        {"$sort": {"_id.ciudad": 1, "total": -1}},
        {"$group": {"_id": "$_id.ciudad", "genero_top": {"$first": "$_id.genero"},
                    "total": {"$first": "$total"}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "ciudad": "$_id", "genero_top": 1, "total": 1}},
    ]
    return list(db.reproducciones.aggregate(pipeline))
