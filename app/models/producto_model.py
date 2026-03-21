from app.database.connection import conectar


def inicializar_tablas_producto():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS producto_media (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo_producto VARCHAR(64) NOT NULL UNIQUE,
            foto_path VARCHAR(255),
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_todos_productos():
    inicializar_tablas_producto()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.*, m.foto_path
        FROM inventario_2026_1___inventary_all p
        LEFT JOIN producto_media m ON m.codigo_producto = p.CODIGO
        """
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def obtener_producto_por_codigo(codigo):
    inicializar_tablas_producto()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.*, m.foto_path
        FROM inventario_2026_1___inventary_all p
        LEFT JOIN producto_media m ON m.codigo_producto = p.CODIGO
        WHERE p.CODIGO=%s
        """,
        (codigo,),
    )
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data


def obtener_familias_y_tipos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM familias")
    familias = cursor.fetchall()
    cursor.execute("SELECT * FROM tipos")
    tipos = cursor.fetchall()
    cursor.close()
    conn.close()
    return familias, tipos


def buscar_productos_por_familia_tipo(familia, tipo):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT CODIGO, NOMBRE
        FROM inventario_2026_1___inventary_all
        WHERE CODIGO LIKE %s
        """,
        (f"{familia}-{tipo}-%",),
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def obtener_ultimo_correlativo(familia, tipo):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT MAX(CAST(SUBSTRING_INDEX(CODIGO, '-', -1) AS UNSIGNED)) AS ultimo
        FROM inventario_2026_1___inventary_all
        WHERE CODIGO LIKE %s
        """,
        (f"{familia}-{tipo}-%",),
    )
    ultimo = cursor.fetchone()["ultimo"] or 0
    cursor.close()
    conn.close()
    return ultimo


def crear_producto(codigo, nombre, stock, ubicacion, ruta_qr, foto_path=None):
    inicializar_tablas_producto()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO inventario_2026_1___inventary_all
        (CODIGO, NOMBRE, STOCK, UBICACION, QR_PATH)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (codigo, nombre, stock, ubicacion, ruta_qr),
    )
    if foto_path:
        cursor.execute(
            """
            INSERT INTO producto_media (codigo_producto, foto_path)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE foto_path=VALUES(foto_path)
            """,
            (codigo, foto_path),
        )
    conn.commit()
    cursor.close()
    conn.close()


def borrar_producto(codigo):
    inicializar_tablas_producto()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM producto_media WHERE codigo_producto=%s", (codigo,))
    cursor.execute("DELETE FROM inventario_2026_1___inventary_all WHERE CODIGO=%s", (codigo,))
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_stock_producto(codigo, stock):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE inventario_2026_1___inventary_all SET STOCK=%s WHERE CODIGO=%s",
        (stock, codigo),
    )
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0
