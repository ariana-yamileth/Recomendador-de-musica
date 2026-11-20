// Consultas del recomendador de musica.
// Ejecutar todas:   mongosh musica_recomendador consultas/consultas.js
// O copiar una por una en MongoDB Compass / mongosh.

function titulo(t) { print("\n=== " + t + " ==="); }

// ---------- A) Quien escucho esto tambien escucho... ----------
titulo("A) Quien escucho la cancion 15 tambien escucho");
const cancion = 15;
const oyentes = db.reproducciones.distinct("usuario_id", { cancion_id: cancion });
printjson(db.reproducciones.aggregate([
  { $match: { usuario_id: { $in: oyentes }, cancion_id: { $ne: cancion } } },
  { $group: { _id: "$cancion_id", oyentes: { $addToSet: "$usuario_id" } } },
  { $project: { total: { $size: "$oyentes" } } },
  { $sort: { total: -1 } },
  { $limit: 10 },
  { $lookup: { from: "canciones", localField: "_id", foreignField: "_id", as: "c" } },
  { $unwind: "$c" },
  { $project: { _id: 0, titulo: "$c.titulo", artista: "$c.artista",
                genero: "$c.genero", total: 1 } }
]).toArray());

// ---------- B) Recomendaciones personalizadas (filtrado colaborativo) ----------
titulo("B) Recomendaciones para el usuario 1");
const yo = 1;
const mis = db.reproducciones.distinct("cancion_id", { usuario_id: yo });
printjson(db.reproducciones.aggregate([
  { $match: { cancion_id: { $in: mis }, usuario_id: { $ne: yo } } },
  { $group: { _id: "$usuario_id", en_comun: { $sum: 1 } } },
  { $sort: { en_comun: -1 } },
  { $limit: 50 },
  { $lookup: { from: "reproducciones", localField: "_id",
               foreignField: "usuario_id", as: "r" } },
  { $unwind: "$r" },
  { $match: { "r.cancion_id": { $nin: mis } } },
  { $group: { _id: "$r.cancion_id", puntaje: { $sum: "$en_comun" } } },
  { $sort: { puntaje: -1 } },
  { $limit: 10 },
  { $lookup: { from: "canciones", localField: "_id", foreignField: "_id", as: "c" } },
  { $unwind: "$c" },
  { $project: { _id: 0, titulo: "$c.titulo", artista: "$c.artista",
                genero: "$c.genero", puntaje: 1 } }
]).toArray());

// ---------- C) Artistas relacionados ----------
titulo("C) Quien escucha al artista 10 tambien escucha a");
const artista = 10;
const fans = db.reproducciones.distinct("usuario_id", { artista_id: artista });
printjson(db.reproducciones.aggregate([
  { $match: { usuario_id: { $in: fans }, artista_id: { $ne: artista } } },
  { $group: { _id: "$artista_id", fans: { $addToSet: "$usuario_id" } } },
  { $project: { total: { $size: "$fans" } } },
  { $sort: { total: -1 } }, { $limit: 5 },
  { $lookup: { from: "artistas", localField: "_id", foreignField: "_id", as: "a" } },
  { $unwind: "$a" },
  { $project: { _id: 0, artista: "$a.nombre", total: 1 } }
]).toArray());

// ---------- D) Top 10 canciones ----------
titulo("D) Top 10 canciones mas escuchadas");
printjson(db.reproducciones.aggregate([
  { $group: { _id: "$cancion_id", reproducciones: { $sum: 1 },
              promedio: { $avg: "$calificacion" } } },
  { $sort: { reproducciones: -1 } }, { $limit: 10 },
  { $lookup: { from: "canciones", localField: "_id", foreignField: "_id", as: "c" } },
  { $unwind: "$c" },
  { $project: { _id: 0, titulo: "$c.titulo", artista: "$c.artista",
                reproducciones: 1, promedio: { $round: ["$promedio", 2] } } }
]).toArray());

// ---------- E) Genero mas escuchado por ciudad ----------
titulo("E) Genero mas escuchado por ciudad");
printjson(db.reproducciones.aggregate([
  { $lookup: { from: "usuarios", localField: "usuario_id",
               foreignField: "_id", as: "u" } },
  { $unwind: "$u" },
  { $group: { _id: { ciudad: "$u.ciudad", genero: "$genero" }, total: { $sum: 1 } } },
  { $sort: { "_id.ciudad": 1, total: -1 } },
  { $group: { _id: "$_id.ciudad", genero_top: { $first: "$_id.genero" },
              total: { $first: "$total" } } },
  { $sort: { _id: 1 } }
]).toArray());

// ---------- F) CRUD y filtros simples ----------
titulo("F) Consultas simples");
printjson(db.canciones.find({ genero: "Rock", anio: { $gte: 2010 } }).limit(5).toArray());
printjson(db.usuarios.find({ generos_favoritos: "Jazz", edad: { $lt: 25 } }).limit(5).toArray());
// Escritura (descomentar para probar):
// db.usuarios.updateOne({ _id: 1 }, { $push: { generos_favoritos: "Indie" } })
// db.reproducciones.deleteMany({ calificacion: 1 })

// ---------- G) Rendimiento: ejecutar con y sin indice ----------
titulo("G) explain de la consulta por usuario");
const ex = db.reproducciones.find({ usuario_id: 1 }).explain("executionStats");
print("Docs examinados: " + ex.executionStats.totalDocsExamined +
      " | Tiempo (ms): " + ex.executionStats.executionTimeMillis);
// Para comparar: db.reproducciones.dropIndex({usuario_id: 1}) y repetir.
