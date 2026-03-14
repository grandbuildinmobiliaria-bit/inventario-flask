# Revisión de la app `inventario-flask`

Fecha: 2026-03-14

## Lo que ya está bien
- Estructura modular por capas (`routes`, `models`, `services`, `integrations`) y patrón `create_app()`.
- Health checks disponibles (`/health` y `/health/db`).
- Separación básica de permisos por rol con decoradores (`login_required`, `role_required`).
- Integración opcional con Google Drive para proyectos.

## Qué te falta o qué podrías agregar

### 1) Seguridad (prioridad alta)
1. **Hashear contraseñas de usuarios** (bcrypt/werkzeug) y nunca guardarlas en texto plano.
2. **CSRF protection** en formularios (`Flask-WTF` o token manual).
3. **Cookies de sesión seguras**: `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SECURE=True` (en prod), `SESSION_COOKIE_SAMESITE='Lax'`.
4. **Secret key fuerte en producción** y eliminar fallback débil (`dev-secret`).
5. **Rate limit** al login (ej. `Flask-Limiter`) para reducir intentos de fuerza bruta.

### 2) Robustez y calidad de datos
1. **Validación de inputs** en backend (no confiar sólo en formulario).
2. **Manejo transaccional** en operaciones de inventario/aprobación para evitar inconsistencias parciales.
3. **Reglas de negocio para stock**: impedir que `STOCK` quede negativo a nivel SQL/servicio.
4. **Unicidad e índices** en columnas clave (`CODIGO`, `username`, etc.).

### 3) Observabilidad y operación
1. **Logging estructurado** (INFO/WARN/ERROR) con trazas de errores.
2. **Métricas básicas**: logins fallidos, solicitudes aprobadas, rechazos, stock crítico.
3. **Manejo de errores global** (`@app.errorhandler`) para respuestas consistentes.

### 4) Producto / UX
1. **Búsqueda avanzada y filtros** por código, nombre, familia, tipo, ubicación.
2. **Paginación** en listados largos (`/lista_productos`, `/solicitudes`, `/usuarios`).
3. **Historial/auditoría** de movimientos (quién, cuándo, cuánto, motivo).
4. **Exportación CSV/Excel/PDF** para inventario y solicitudes.
5. **Alertas de stock bajo** (correo/WhatsApp/Slack opcional).

### 5) DevEx y mantenimiento
1. **README completo** (setup, variables de entorno, estructura, comandos).
2. **Pruebas automáticas** (pytest): unitarias para services y de integración para rutas.
3. **CI/CD** (GitHub Actions): lint + tests + build.
4. **Migraciones DB** (`Flask-Migrate/Alembic`) en vez de cambios manuales.
5. **Entornos** (dev/staging/prod) con configuración explícita.

## Backlog sugerido (rápido)

### Sprint 1 (impacto inmediato)
- Hash de contraseñas + actualización de login.
- CSRF y endurecimiento de cookies/sesión.
- README + `.env.example`.

### Sprint 2
- Tests base (login, crear producto, confirmar salida).
- Logging + manejo de errores global.
- Índices/constraints de DB.

### Sprint 3
- Historial de movimientos + exportaciones.
- Paginación/filtros completos.
- Alertas de stock bajo.
