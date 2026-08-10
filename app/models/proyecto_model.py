from app.database.connection import conectar


def asegurar_columna_distrito_lima():
    """Agrega ubicación distrital a proyectos si la tabla todavía no la tiene."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'proyectos'
          AND COLUMN_NAME = 'distrito_lima'
        """
    )
    existe = cursor.fetchone()["total"] > 0
    if not existe:
        cursor.close()
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE proyectos ADD COLUMN distrito_lima VARCHAR(80) NULL AFTER cliente")
        conn.commit()
    cursor.close()
    conn.close()


def guardar_drive_folder_id(codigo, nombre, cliente, drive_folder_id, estado="activo", distrito_lima=None):
    """Guarda (insert/update) el folder id de Google Drive para un proyecto."""
    asegurar_columna_distrito_lima()
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM proyectos WHERE codigo=%s", (codigo,))
    row = cursor.fetchone()

    if row:
        cursor.execute(
            """
            UPDATE proyectos
            SET nombre=%s, cliente=%s, distrito_lima=%s, drive_folder_id=%s, estado=%s
            WHERE codigo=%s
            """,
            (nombre, cliente, distrito_lima, drive_folder_id, estado, codigo),
        )
    else:
        cursor.execute(
            """
            INSERT INTO proyectos (codigo, nombre, cliente, distrito_lima, drive_folder_id, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (codigo, nombre, cliente, distrito_lima, drive_folder_id, estado),
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
    asegurar_columna_distrito_lima()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT codigo, nombre, cliente, distrito_lima, drive_folder_id, estado
        FROM proyectos
        ORDER BY id DESC
        """
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def obtener_proyecto_por_codigo(codigo):
    """Obtiene un proyecto específico por su código."""
    asegurar_columna_distrito_lima()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT codigo, nombre, cliente, distrito_lima, drive_folder_id, estado
        FROM proyectos
        WHERE codigo=%s
        """,
        (codigo,),
    )
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data


def actualizar_proyecto(codigo, nombre, cliente, drive_folder_id, estado, distrito_lima=None):
    """Actualiza metadata del proyecto por código."""
    asegurar_columna_distrito_lima()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE proyectos
        SET nombre=%s, cliente=%s, distrito_lima=%s, drive_folder_id=%s, estado=%s
        WHERE codigo=%s
        """,
        (nombre, cliente, distrito_lima, drive_folder_id, estado, codigo),
    )
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0


def eliminar_proyecto_por_codigo(codigo):
    """Elimina proyecto por código."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proyectos WHERE codigo=%s", (codigo,))
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0


def obtener_proyectos_para_mapa():
    """Lista proyectos con distrito para mostrarlos como referencia en el mapa."""
    asegurar_columna_distrito_lima()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT codigo, nombre, cliente, distrito_lima, estado
        FROM proyectos
        WHERE estado <> 'cerrado'
        ORDER BY nombre ASC
        """
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
