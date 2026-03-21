# Paso a paso: interfaz para crear, editar, eliminar y abrir proyectos en Google Drive

## 1) Configura variables de entorno
En tu `.env` define:

- `GOOGLE_SERVICE_ACCOUNT_FILE=/ruta/a/credenciales.json`
- `GOOGLE_DRIVE_PARENT_FOLDER_ID=id_carpeta_padre_drive`

Opcional pero recomendado:
- `BASE_URL=http://localhost:5000`
- `SECRET_KEY=una_clave_larga_y_segura`

## 2) Inicia sesión como admin
La pantalla de creación/listado/edición/eliminación de proyectos está protegida por rol `admin`.

## 3) Entra al módulo de proyectos
Desde Inicio, usa:
- **📁 Crear proyecto Drive** para registrar uno nuevo.
- **📂 Ver proyectos** para revisar y operar sobre los existentes.

## 4) Crear proyecto (`/proyectos/crear`)
Completa:
- Código (ej: `PRJ-001`)
- Cliente
- Nombre del proyecto
- Estado inicial (`activo`, `pausado`, `cerrado`)

Al guardar:
1. Se crea la carpeta raíz en Drive con formato `cliente - codigo - nombre`.
2. Se crean subcarpetas automáticas: `Planos`, `Compras`, `Guías`, `Evidencias`, `Cierre`.
3. Se guarda/actualiza en DB con `drive_folder_id`.

## 5) Ver y operar proyectos (`/proyectos`)
En la tabla verás: código, nombre, cliente, estado y `drive_folder_id`.

Acciones disponibles por fila:
- **📂 Abrir Drive**: abre la carpeta del proyecto en Google Drive.
- **✏️ Editar**: modifica código/nombre/cliente/estado en DB.
- **🗑️ Eliminar**: borra el registro en DB (con confirmación).

## 6) Editar proyecto (`/proyectos/editar/<codigo>`)
Puedes cambiar metadata del proyecto:
- código
- nombre
- cliente
- estado

> Nota: editar **no** recrea ni renombra carpeta en Google Drive; solo actualiza la base de datos.

## 7) Errores comunes y solución
- **Faltan dependencias de Google**: instala `requirements.txt`.
- **No existe archivo JSON**: revisa `GOOGLE_SERVICE_ACCOUNT_FILE`.
- **No hay permisos en carpeta padre**: comparte la carpeta de Drive con la cuenta de servicio.
- **No aparecen opciones de proyecto**: verifica que el usuario logueado tenga rol `admin`.
