# Recomendador de música · MongoDB Atlas

Proyecto de Bases de Datos No Relacionales en la nube. Sistema de recomendación
("quien escuchó esto también escuchó…") con **MongoDB Atlas**, datos generados
automáticamente (> 32,000 documentos), administración de roles, y una aplicación
web/API en Python que se conecta y consume los datos de la nube.

## Requisitos
- Python 3.9+
- Cuenta de MongoDB Atlas con un clúster M0 (gratis) → ver `docs/ADMINISTRACION_ATLAS.md`

## Puesta en marcha
```bash
# 1. Entorno virtual e instalación
python -m venv .venv
.venv\Scripts\activate            # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt

# 2. Credenciales: copia .env.example a .env y pon tus usuarios/contraseñas de Atlas
copy .env.example .env            # Mac/Linux: cp .env.example .env

# 3. Comprobar conexión
python scripts/probar_conexion.py

# 4. Generar y cargar los datos automáticamente (~32,100 documentos)
python scripts/generar_datos.py

# 5. Validación de esquema y CRUD
python scripts/validacion.py
python scripts/demo_crud.py

# 6. Administración: probar permisos de cada rol
python scripts/probar_roles.py

# 7. Aplicación web + API
python -m uvicorn app.main:app --reload
#   Web:  http://127.0.0.1:8000
#   API:  http://127.0.0.1:8000/docs
```

## Estructura
| Ruta | Contenido |
|---|---|
| `app/config.py` | Conexión a Atlas desde `.env` (roles admin / app / lectura) |
| `app/main.py` | API REST (CRUD + recomendaciones) |
| `app/consultas.py` | Aggregation pipelines |
| `app/esquemas.py` | Validación `$jsonSchema` |
| `app/static/index.html` | Interfaz web que consume la API |
| `scripts/` | Conexión, carga automática, validación, CRUD, prueba de roles |
| `consultas/consultas.js` | Consultas para mongosh / Compass |
| `docs/` | Guía de administración de Atlas y plantilla del reporte |

## Colecciones
| Colección | Documentos | Descripción |
|---|---|---|
| usuarios | 1,000 | perfil, ciudad, géneros favoritos |
| artistas | 100 | nombre, país, géneros |
| canciones | 1,000 | título, artista (desnormalizado), género, año |
| reproducciones | ~30,000 | usuario, canción, fecha, calificación |

## Consultas en mongosh (opcional)
```bash
mongosh "mongodb+srv://musica-cluster.rx0ossn.mongodb.net/musica_recomendador" --username admin_proyecto consultas/consultas.js
```

## Integrantes
- 

> Todos los datos son ficticios (Faker). Nunca subas `.env` a GitHub.
