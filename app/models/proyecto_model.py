from app.database.connection import conectar


def guardar_drive_folder_id(codigo, nombre, cliente, drive_folder_id, estado="activo"):
    """Guarda (insert/update) el folder id de Google Drive para un proyecto."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM proyectos WHERE codigo=%s", (codigo,))
    row = cursor.fetchone()

    if row:
        cursor.execute(
            """
            UPDATE proyectos
            SET nombre=%s, cliente=%s, drive_folder_id=%s, estado=%s
            WHERE codigo=%s
            """,
            (nombre, cliente, drive_folder_id, estado, codigo),
        )
    else:
        cursor.execute(
            """
            INSERT INTO proyectos (codigo, nombre, cliente, drive_folder_id, estado)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (codigo, nombre, cliente, drive_folder_id, estado),
        )

    conn.commit()
    cursor.close()
    conn.close()


def obtener_drive_folder_id_por_codigo(codigo):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT drive_folder_id FROM proyectos WHERE codigo=%s", (codigo,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row["drive_folder_id"] if row else None


def obtener_proyectos():
    """Lista proyectos registrados para mostrar en la interfaz."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT codigo, nombre, cliente, drive_folder_id, estado
        FROM proyectos
        ORDER BY id DESC
        """
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def obtener_proyecto_por_codigo(codigo):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT codigo, nombre, cliente, drive_folder_id, estado
        FROM proyectos
        WHERE codigo=%s
        """,
        (codigo,),
    )
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data


def actualizar_proyecto(codigo_original, codigo, nombre, cliente, estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE proyectos
        SET codigo=%s, nombre=%s, cliente=%s, estado=%s
        WHERE codigo=%s
        """,
        (codigo, nombre, cliente, estado, codigo_original),
    )
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_proyecto_por_codigo(codigo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proyectos WHERE codigo=%s", (codigo,))
    conn.commit()
    cursor.close()
    conn.close()
