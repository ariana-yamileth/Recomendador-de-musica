# Reporte del proyecto: Recomendador de música con MongoDB Atlas

**Integrantes:**  
**Materia:** Bases de datos no relacionales en la nube  **Fecha:**

## 1. Bases de datos no relacionales en la nube
### Características y ventajas
Esquema flexible, escalabilidad horizontal, alta disponibilidad con réplicas, sin servidores propios que mantener, acceso desde cualquier lugar y respaldos/monitoreo integrados.

### Tipos de gestores
| Tipo | Funcionamiento | Ejemplo | Idóneo para |
|---|---|---|---|
| Orientada a **documentos** | Documentos JSON/BSON flexibles | **MongoDB** | Perfiles, catálogos, apps web |
| Orientada a **columnas** | Familias de columnas, escrituras masivas | Cassandra | Logs, series de tiempo |
| Orientada a **grafos** | Nodos y relaciones | Neo4j | Redes y recomendaciones muy conectadas |
| Orientada a **objetos** | Objetos del lenguaje de programación | db4o | Modelos de objetos complejos |

### Selección del gestor
Se eligió **MongoDB Atlas** (documentos): usuarios, canciones y reproducciones son documentos con listas internas (`generos_favoritos`), las recomendaciones se resuelven con aggregation pipelines y Atlas ofrece nivel gratuito en la nube. Un grafo sería más natural para recomendar, pero MongoDB sigue siendo viable (evidencia: consultas A y B).

**Implementación:** clúster M0 `musica-cluster` en AWS. *(Captura del clúster activo.)*

## 2. Creación de bases de datos en la nube
Base `musica_recomendador` con 4 colecciones creadas por `scripts/generar_datos.py` (`create_collection` con validador), índices con `create_index`.
- Modelo: `usuarios` (1,000), `artistas` (100), `canciones` (1,000), `reproducciones` (~30,000). Total > 32,000 documentos.
- **Desnormalización:** el nombre del artista se copia dentro de `canciones` para evitar un `$lookup` en cada listado.
- **Automatización:** los datos se generan con Faker y se cargan por lotes con `insert_many`. *(Captura de la salida del script.)*

## 3. Manipulación de datos
- **Create:** `insert_one` / `POST /api/canciones`
- **Read:** `find`, filtros, agregaciones / `GET /api/canciones`, `/api/top-canciones`, `/api/recomendaciones/{id}`
- **Update:** `update_one` con `$set` / `PUT /api/canciones/{id}`
- **Delete:** `delete_one`, `delete_many` / `DELETE /api/canciones/{id}`
- Validación de esquema: `scripts/validacion.py` *(captura de rechazos)*.
- Rendimiento: comparar `explain("executionStats")` con y sin índice (final de `consultas/consultas.js`).

## 4. Administración de bases de datos
Ver `docs/ADMINISTRACION_ATLAS.md`. Tres usuarios (admin, readWrite, read), lista de IP permitidas y prueba con `scripts/probar_roles.py`. *(Capturas de Database Access, Network Access y salida de probar_roles.)*

## 5. Conexión a la base de datos en la nube
La aplicación (FastAPI) se integra con Atlas mediante el driver oficial **PyMongo** y una cadena `mongodb+srv://` leída desde `.env` (`app/config.py`). La aplicación usa el usuario de rol `readWrite`, no el administrador.

## 6. Consumo de datos en la nube
API REST (`app/main.py`) y una interfaz web (`app/static/index.html`) que consume los endpoints con `fetch`. Documentación interactiva automática en `/docs`. *(Capturas de la web y de `/docs`.)*

## 7. Dimensión socioafectiva
- **Razonamiento crítico, lógico y matemático:** diseño del filtrado colaborativo (usuarios con canciones en común ponderan el puntaje).
- **Trabajo en equipo:** repartir roles (BD/Atlas, scripts, API y web, documentación) y registrar quién hizo qué.
- **Gestión de la información:** reportes de top canciones y género por ciudad para apoyar decisiones.
- **Ética y responsabilidad:** datos 100 % ficticios (Faker), credenciales fuera del código, mínimo privilegio en los usuarios.

## 8. Conclusiones
*(Escribe aquí lo aprendido, dificultades y mejoras posibles.)*
