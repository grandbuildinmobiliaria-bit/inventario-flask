from app.database.connection import conectar


def obtener_resumen_home():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM inventario_2026_1___inventary_all")
    total_productos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as bajos FROM inventario_2026_1___inventary_all WHERE STOCK < 5")
    stock_bajo = cursor.fetchone()["bajos"]

    cursor.execute("SELECT COUNT(*) as total FROM solicitudes")
    solicitudes_pendientes = cursor.fetchone()["total"]

    cursor.close()
    conn.close()
    return total_productos, stock_bajo, solicitudes_pendientes


def confirmar_salida_productos(seleccionados):
    conn = conectar()
    cursor = conn.cursor()
    for p in seleccionados:
        cursor.execute(
            """
            UPDATE inventario_2026_1___inventary_all
            SET STOCK = STOCK - %s, UBICACION=%s
            WHERE CODIGO=%s
            """,
            (p["cantidad"], p["ubicacion"], p["CODIGO"]),
        )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_solicitudes():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM solicitudes ORDER BY fecha DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def insertar_solicitudes(usuario, seleccionados, fecha):
    conn = conectar()
    cursor = conn.cursor()
    for p in seleccionados:
        cursor.execute(
            """
            INSERT INTO solicitudes (usuario, codigo_producto, nombre_producto, cantidad, ubicacion, qr_path, fecha)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (usuario, p["CODIGO"], p["NOMBRE"], p["cantidad"], p["ubicacion"], p.get("QR_PATH"), fecha),
        )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_solicitudes_por_id():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM solicitudes ORDER BY id ASC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def aprobar_solicitudes(solicitudes):
    conn = conectar()
    cursor = conn.cursor()
    for s in solicitudes:
        cursor.execute(
            """
            UPDATE inventario_2026_1___inventary_all
            SET STOCK = STOCK - %s
            WHERE CODIGO = %s
            """,
            (s["cantidad"], s["codigo_producto"]),
        )
    cursor.execute("DELETE FROM solicitudes")
    conn.commit()
    cursor.close()
    conn.close()


def rechazar_solicitud(solicitud_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM solicitudes WHERE id=%s", (solicitud_id,))
    conn.commit()
    cursor.close()
    conn.close()
