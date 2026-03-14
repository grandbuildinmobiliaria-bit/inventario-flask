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
