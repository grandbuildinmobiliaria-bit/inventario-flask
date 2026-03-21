from flask import current_app
import os
import qrcode

from app.models import producto_model


def generar_qr(codigo):
    base_url = current_app.config.get("BASE_URL", "http://localhost:5000").rstrip("/")
    url = f"{base_url}/producto/{codigo}"
    img = qrcode.make(url)
    ruta_relativa = f"qr/{codigo}.png"
    ruta_completa = os.path.join("static", ruta_relativa)
    os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
    img.save(ruta_completa)
    return ruta_relativa


def crear_producto_desde_form(familia, tipo, nombre, stock, ubicacion, foto_path=None):
    ultimo = producto_model.obtener_ultimo_correlativo(familia, tipo)
    codigo = f"{familia}-{tipo}-{(ultimo + 1):03d}"
    ruta_qr = generar_qr(codigo)
    producto_model.crear_producto(codigo, nombre, stock, ubicacion, ruta_qr, foto_path=foto_path)
    return codigo
