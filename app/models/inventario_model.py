from app.database.connection import conectar


def inicializar_tablas_solicitudes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS solicitudes_historial (
            id INT AUTO_INCREMENT PRIMARY KEY,
            solicitud_id INT,
            usuario VARCHAR(120) NOT NULL,
            codigo_producto VARCHAR(80) NOT NULL,
            nombre_producto VARCHAR(255) NOT NULL,
            cantidad INT NOT NULL,
            ubicacion VARCHAR(120),
            qr_path VARCHAR(255),
            proyecto_codigo VARCHAR(50),
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            fecha_solicitud DATETIME NOT NULL,
            fecha_estado DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    try:
        cursor.execute("ALTER TABLE solicitudes ADD COLUMN proyecto_codigo VARCHAR(50) NULL")
    except Exception:
        pass
    conn.commit()
    cursor.close()
    conn.close()


def obtener_resumen_home():
    inicializar_tablas_solicitudes()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM inventario_2026_1___inventary_all")
    total_productos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as bajos FROM inventario_2026_1___inventary_all WHERE STOCK < 5")
    stock_bajo = cursor.fetchone()["bajos"]

    cursor.execute("SELECT COUNT(*) as total FROM solicitudes_historial WHERE estado='pendiente'")
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
    inicializar_tablas_solicitudes()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM solicitudes ORDER BY fecha DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def insertar_solicitudes(usuario, seleccionados, fecha):
    inicializar_tablas_solicitudes()
    conn = conectar()
    cursor = conn.cursor()
    for p in seleccionados:
        cursor.execute(
            """
            INSERT INTO solicitudes (usuario, codigo_producto, nombre_producto, cantidad, ubicacion, qr_path, fecha, proyecto_codigo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                usuario,
                p["CODIGO"],
                p["NOMBRE"],
                p["cantidad"],
                p["ubicacion"],
                p.get("QR_PATH"),
                fecha,
                p.get("proyecto_codigo"),
            ),
        )
        solicitud_id = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO solicitudes_historial
                (solicitud_id, usuario, codigo_producto, nombre_producto, cantidad, ubicacion, qr_path, proyecto_codigo, estado, fecha_solicitud, fecha_estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pendiente', %s, %s)
            """,
            (
                solicitud_id,
                usuario,
                p["CODIGO"],
                p["NOMBRE"],
                p["cantidad"],
                p["ubicacion"],
                p.get("QR_PATH"),
                p.get("proyecto_codigo"),
                fecha,
                fecha,
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_solicitudes_por_id():
    inicializar_tablas_solicitudes()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM solicitudes ORDER BY id ASC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def aprobar_solicitudes(solicitudes):
    inicializar_tablas_solicitudes()
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
        cursor.execute(
            """
            UPDATE solicitudes_historial
            SET estado='aprobada', fecha_estado=NOW()
            WHERE solicitud_id=%s AND estado='pendiente'
            """,
            (s["id"],),
        )
    cursor.execute("DELETE FROM solicitudes")
    conn.commit()
    cursor.close()
    conn.close()


def rechazar_solicitud(solicitud_id):
    inicializar_tablas_solicitudes()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE solicitudes_historial
        SET estado='rechazada', fecha_estado=NOW()
        WHERE solicitud_id=%s AND estado='pendiente'
        """,
        (solicitud_id,),
    )
    cursor.execute("DELETE FROM solicitudes WHERE id=%s", (solicitud_id,))
    conn.commit()
    cursor.close()
    conn.close()


def obtener_historial_solicitudes_por_usuario(usuario):
    inicializar_tablas_solicitudes()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT usuario, codigo_producto, nombre_producto, cantidad, ubicacion, proyecto_codigo,
               estado, fecha_solicitud, fecha_estado
        FROM solicitudes_historial
        WHERE usuario=%s
        ORDER BY fecha_solicitud DESC
        """,
        (usuario,),
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
