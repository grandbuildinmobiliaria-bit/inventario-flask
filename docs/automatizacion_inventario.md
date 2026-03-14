# Automatización y siguientes integraciones para Inventario Flask

## 1) Evaluación rápida de la estructura actual

La base actual **sí es válida para un MVP funcional**:

- Flujo de autenticación y sesión.
- Roles (`admin`, `operador`) para separar permisos.
- CRUD principal de productos.
- Flujo de solicitudes para aprobación.
- Generación de QR por producto.

### Hallazgos importantes para escalar con menos trabajo manual

1. **`app.py` concentra toda la lógica** (rutas, acceso a datos y reglas de negocio).
2. **Contraseñas en texto plano** (riesgo alto de seguridad).
3. **Sin trazabilidad completa de movimientos** (solo queda stock final, no historial detallado por transacción).
4. **Operaciones críticas sin transacciones explícitas robustas** para escenarios concurrentes.
5. **Código de QR fijo a `localhost`**, lo que puede fallar en hosting real.

---

## 2) Integraciones recomendadas (prioridad alta)

## A. Google Drive (proyectos de obra)

Con `service account` vas por muy buen camino. Para construcción, lo más útil es:

- Crear carpeta raíz por cliente/proyecto.
- Subcarpetas automáticas: `Planos`, `Compras`, `Guías`, `Evidencias`, `Cierre`.
- Guardar en BD el `drive_folder_id` para reutilizar vínculos.
- Permisos automáticos por rol (solo lectura para campo, edición para administración).

**Sugerencia técnica mínima:**

- Tabla `proyectos`:
  - `id`, `codigo`, `nombre`, `cliente`, `drive_folder_id`, `fecha_creacion`, `estado`.
- Trigger de negocio en app:
  - Al crear proyecto en Flask -> crear carpeta en Drive -> guardar `drive_folder_id`.

## B. Kardex / historial de movimientos

Agregar tabla de movimientos para auditoría:

- `movimientos_inventario`: `id`, `fecha`, `usuario`, `tipo` (`entrada`, `salida`, `ajuste`), `codigo_producto`, `cantidad`, `motivo`, `proyecto_id`, `origen`.

Esto permite:

- Saber **quién movió qué y cuándo**.
- Reportes por proyecto, semana, cuadrilla.
- Reducir retrabajo en cierres mensuales.

## C. Alertas automáticas

- Alertas de stock mínimo por WhatsApp/Telegram/email.
- Resumen diario al administrador: solicitudes pendientes, productos críticos, top consumos.

## D. Reabastecimiento sugerido

Regla simple inicial:

- Punto de pedido = consumo promedio diario × lead time + stock de seguridad.
- La app propone lista de compra automáticamente.

## E. Integración con documentos de salida

- Generar PDF de vale/boleta por despacho.
- Guardarlo automáticamente en carpeta del proyecto en Drive.
- Enviar link al responsable de obra.

---

## 3) Mejoras técnicas clave (antes de crecer)

1. **Modularizar la app**:
   - `routes/`, `services/`, `repositories/`, `models/`.
2. **Seguridad**:
   - Hash de contraseñas (`werkzeug.security` o `bcrypt`).
3. **Config por entorno**:
   - Variables para `BASE_URL`, `DB`, `DRIVE_PARENT_FOLDER_ID`.
4. **Transacciones y validación concurrente**:
   - Confirmar stock en `UPDATE` con condición de disponibilidad.
5. **Logs y métricas**:
   - Registrar errores y eventos de negocio.

---

## 4) Roadmap recomendado (4 etapas)

### Etapa 1 (rápida, alto impacto)

- Contraseñas con hash.
- Tabla de movimientos.
- Alertas de stock bajo.

### Etapa 2

- Módulo de proyectos + creación automática de carpetas en Drive.
- Asociación de salidas de inventario a proyecto.

### Etapa 3

- PDF de despachos + guardado automático en Drive.
- Dashboard de consumo por proyecto.

### Etapa 4

- Pronóstico básico de consumo y sugerencias de compra.
- Integración con herramientas contables/ERP (si aplica).

---

## 5) KPI para medir ahorro de tiempo

- Tiempo promedio de despacho (antes vs después).
- % de solicitudes aprobadas sin correcciones.
- Quiebres de stock por mes.
- Horas administrativas dedicadas a cierres de inventario.
- Diferencia inventario teórico vs físico.

Estos indicadores te dirán si la automatización realmente está reduciendo carga operativa.
