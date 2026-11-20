# Administración en MongoDB Atlas (usuarios, roles y niveles de acceso)

> Los nombres de menús de Atlas pueden variar un poco según el idioma y la versión.
> Ruta general: menú izquierdo → **Seguridad → Acceso a bases de datos y redes**.

## 1. Usuarios de base de datos (control de permisos)

Crea **tres** usuarios. Pestaña **Usuarios de bases de datos → Agregar nuevo usuario de base de datos**,
método *Contraseña* (usa contraseñas solo con letras y números para evitar problemas en la URI).

| Usuario | Privilegios en Atlas | Para qué se usa | Variable en `.env` |
|---|---|---|---|
| `admin_proyecto` | Rol integrado **Atlas admin** | Cargar datos, crear colecciones, índices | `MONGO_URI` |
| `app_escritura` | Privilegios específicos: rol **readWrite**, base `musica_recomendador` | La API (CRUD y recomendaciones) | `MONGO_URI_APP` |
| `app_lectura` | Privilegios específicos: rol **read**, base `musica_recomendador` | Reportes y consultas sin riesgo de modificar | `MONGO_URI_LECTURA` |

En *Privilegios de base de datos* usa **Agregar privilegios específicos** (no el rol "cualquier base de datos"):
selecciona el rol `readWrite` o `read` y escribe `musica_recomendador` como base de datos.
Opcional: en *Restringir acceso a recursos específicos* limita cada usuario a tu clúster.

> Principio de **mínimo privilegio**: cada componente solo recibe el acceso que necesita.

## 2. Acceso de red (Network Access / IP Access List)

Pestaña **Acceso a la red → Agregar dirección IP**: agrega tu IP actual. Evita `0.0.0.0/0`.
Si cambias de red (casa, escuela), agrega la nueva IP.

## 3. Cadenas de conexión

Para cada usuario, la URI es la misma con distinto usuario y contraseña:
`mongodb+srv://USUARIO:PASSWORD@musica-cluster.rx0ossn.mongodb.net/?retryWrites=true&w=majority`
Cópialas en tu `.env` (plantilla en `.env.example`).

## 4. Verificar que los permisos funcionan

```bash
python scripts/probar_roles.py
```
Resultado esperado en Atlas (esto es evidencia para el reporte):

| Acción | administrador | aplicación | solo lectura |
|---|---|---|---|
| Leer canciones | PERMITIDO | PERMITIDO | PERMITIDO |
| Escribir documentos | PERMITIDO | PERMITIDO | **RECHAZADO** (código 13) |
| Ver otras bases (admin, local) | PERMITIDO (ve más bases) | solo `musica_recomendador` | solo `musica_recomendador` |

## 5. Otras medidas de seguridad aplicadas
- Credenciales en `.env`, excluido de Git con `.gitignore`.
- Validación de esquema (`$jsonSchema`) que rechaza datos inválidos (`python scripts/validacion.py`).
- La API devuelve 403 si el rol no tiene permiso y 422 si el documento no pasa la validación.
- Conexión cifrada (TLS) por defecto con `mongodb+srv://`.
