from datetime import datetime

from app.models import inventario_model
from app.models import proyecto_model
from app.integrations.google_drive import GoogleDriveIntegration


def enviar_solicitud(usuario, seleccionados):
    inventario_model.insertar_solicitudes(usuario, seleccionados, datetime.now())


def aprobar_todas_solicitudes():
    solicitudes = inventario_model.obtener_solicitudes_por_id()
    if solicitudes:
        inventario_model.aprobar_solicitudes(solicitudes)
        _guardar_boletas_en_drive_por_proyecto(solicitudes)
    return solicitudes


def _guardar_boletas_en_drive_por_proyecto(solicitudes):
    """Sube resumen de boleta a la carpeta de Drive del proyecto (si existe)."""
    agrupadas = {}
    for s in solicitudes:
        proyecto = s.get("proyecto_codigo") or "sin-proyecto"
        agrupadas.setdefault(proyecto, []).append(s)

    integration = GoogleDriveIntegration()
    for proyecto_codigo, items in agrupadas.items():
        if proyecto_codigo == "sin-proyecto":
            continue
        proyecto = proyecto_model.obtener_proyecto_por_codigo(proyecto_codigo)
        folder_id = proyecto.get("drive_folder_id") if proyecto else None
        if not folder_id:
            continue

        fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        lineas = [f"Boleta de salida - Proyecto {proyecto_codigo}", f"Fecha: {fecha}", ""]
        for it in items:
            lineas.append(
                f"{it['codigo_producto']} | {it['nombre_producto']} | Cant: {it['cantidad']} | Ubic: {it['ubicacion']} | Usuario: {it['usuario']}"
            )
        contenido = "\n".join(lineas)
        nombre_archivo = f"boleta_{proyecto_codigo}_{fecha}.txt"
        try:
            integration.subir_texto_a_carpeta(folder_id, nombre_archivo, contenido)
        except Exception:
            continue
