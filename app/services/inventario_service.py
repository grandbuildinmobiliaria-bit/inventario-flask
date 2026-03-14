from datetime import datetime

from app.models import inventario_model


def enviar_solicitud(usuario, seleccionados):
    inventario_model.insertar_solicitudes(usuario, seleccionados, datetime.now())


def aprobar_todas_solicitudes():
    solicitudes = inventario_model.obtener_solicitudes_por_id()
    if solicitudes:
        inventario_model.aprobar_solicitudes(solicitudes)
    return solicitudes
