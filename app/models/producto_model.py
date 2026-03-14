from app.database.connection import conectar


def obtener_todos_productos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario_2026_1___inventary_all")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def obtener_producto_por_codigo(codigo):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario_2026_1___inventary_all WHERE CODIGO=%s", (codigo,))
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


def crear_producto(codigo, nombre, stock, ubicacion, ruta_qr):
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
    conn.commit()
    cursor.close()
    conn.close()


def borrar_producto(codigo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario_2026_1___inventary_all WHERE CODIGO=%s", (codigo,))
    conn.commit()
    cursor.close()
    conn.close()
