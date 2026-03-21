# Paso a paso: flujo completo de proyectos en Google Drive

## 1) Configura variables de entorno
En tu `.env` define:

- `GOOGLE_SERVICE_ACCOUNT_FILE=/ruta/a/credenciales.json`
- `GOOGLE_DRIVE_PARENT_FOLDER_ID=id_carpeta_padre_drive`

Opcional pero recomendado:
- `BASE_URL=http://localhost:5000`
- `SECRET_KEY=una_clave_larga_y_segura`

## 2) Inicia sesión como admin
La pantalla de creación/listado de proyectos está protegida por rol `admin`.

## 3) Entra a la opción nueva del dashboard
Desde Inicio, usa:
- **📁 Crear proyecto Drive** para registrar uno nuevo.
- **📂 Ver proyectos** para revisar los existentes.

## 4) Completa formulario de creación
En `/proyectos/crear` llena:
- Código (ej: `PRJ-001`)
- Cliente
- Nombre del proyecto
- Estado inicial (activo/pausado/cerrado)

## 5) Qué sucede al enviar
Al hacer clic en **Crear en Drive y guardar**:
1. Se crea la carpeta raíz en Drive con formato: `cliente - codigo - nombre`.
2. Se crean subcarpetas automáticas: `Planos`, `Compras`, `Guías`, `Evidencias`, `Cierre`.
3. Se guarda/actualiza el proyecto en DB con `drive_folder_id`.

## 6) Revisa resultados del listado
En `/proyectos` verás tabla con:
- código, nombre, cliente, estado y `drive_folder_id`.
- columna de **Acciones** por cada proyecto.

Botones disponibles:
- **📂 Abrir Drive**: abre la carpeta del proyecto en Google Drive.
- **✏️ Editar**: entra al formulario para actualizar metadata.
- **🗑️ Eliminar**: borra el proyecto (con confirmación previa).

## 7) Editar proyecto existente
Ruta: `/proyectos/editar/<codigo>` (GET/POST).

En el formulario puedes modificar:
- Cliente
- Nombre del proyecto
- `drive_folder_id`
- Estado (activo/pausado/cerrado)

Al guardar, se actualiza el registro en base de datos.

## 8) Eliminar proyecto
Ruta: `/proyectos/eliminar/<codigo>` (POST).

Desde el listado, al confirmar la eliminación:
- se borra el registro del proyecto en DB por código.
- se regresa al listado con mensaje de resultado.

## 9) Abrir carpeta de Drive
Ruta: `/proyectos/abrir/<codigo>` (GET).

El sistema toma `drive_folder_id` del proyecto y redirige a:
- `https://drive.google.com/drive/folders/<drive_folder_id>`

## 10) Errores comunes y solución
- **Faltan dependencias de Google**: instala `requirements.txt`.
- **No existe archivo JSON**: revisa `GOOGLE_SERVICE_ACCOUNT_FILE`.
- **No hay permisos en carpeta padre**: comparte la carpeta de Drive con la cuenta de servicio.
- **No abre opciones de proyecto**: verifica que el usuario logueado tenga rol `admin`.
- **No abre Drive al usar “📂 Abrir Drive”**: confirma que `drive_folder_id` exista y sea válido.
