from app.database.connection import conectar


def inicializar_tablas_contactos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL,
            telefono VARCHAR(30) NOT NULL,
            correo VARCHAR(120),
            ubicacion VARCHAR(120) NOT NULL,
            observaciones VARCHAR(255),
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cliente_proyectos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            proyecto_codigo VARCHAR(50) NOT NULL,
            UNIQUE KEY unique_cliente_proyecto (cliente_id, proyecto_codigo),
            CONSTRAINT fk_cliente_proyecto_cliente FOREIGN KEY (cliente_id)
                REFERENCES clientes(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS proveedores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL,
            telefono VARCHAR(30) NOT NULL,
            tipo_productos VARCHAR(160) NOT NULL,
            ruc VARCHAR(20) NOT NULL,
            ubicacion VARCHAR(120) NOT NULL,
            correo VARCHAR(120),
            observaciones VARCHAR(255),
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


def obtener_proyectos_disponibles():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT codigo, nombre FROM proyectos ORDER BY codigo ASC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def obtener_clientes(busqueda=None):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT c.id, c.nombre, c.telefono, c.correo, c.ubicacion, c.observaciones,
               COUNT(cp.id) AS total_proyectos,
               GROUP_CONCAT(cp.proyecto_codigo ORDER BY cp.proyecto_codigo SEPARATOR ', ') AS proyectos
        FROM clientes c
        LEFT JOIN cliente_proyectos cp ON cp.cliente_id = c.id
    """
    params = []
    if busqueda:
        query += " WHERE c.nombre LIKE %s OR c.ubicacion LIKE %s "
        like = f"%{busqueda}%"
        params.extend([like, like])

    query += " GROUP BY c.id ORDER BY c.id DESC"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def obtener_cliente_por_id(cliente_id):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, nombre, telefono, correo, ubicacion, observaciones
        FROM clientes
        WHERE id=%s
        """,
        (cliente_id,),
    )
    row = cursor.fetchone()

    cursor.execute(
        "SELECT proyecto_codigo FROM cliente_proyectos WHERE cliente_id=%s ORDER BY proyecto_codigo",
        (cliente_id,),
    )
    proyectos = [r["proyecto_codigo"] for r in cursor.fetchall()]

    cursor.close()
    conn.close()
    if row:
        row["proyectos"] = proyectos
    return row


def crear_cliente(data):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO clientes (nombre, telefono, correo, ubicacion, observaciones)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (data["nombre"], data["telefono"], data.get("correo"), data["ubicacion"], data.get("observaciones")),
    )
    cliente_id = cursor.lastrowid

    for codigo in data.get("proyectos", []):
        cursor.execute(
            "INSERT IGNORE INTO cliente_proyectos (cliente_id, proyecto_codigo) VALUES (%s, %s)",
            (cliente_id, codigo),
        )

    conn.commit()
    cursor.close()
    conn.close()


def actualizar_cliente(cliente_id, data):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE clientes
        SET nombre=%s, telefono=%s, correo=%s, ubicacion=%s, observaciones=%s
        WHERE id=%s
        """,
        (data["nombre"], data["telefono"], data.get("correo"), data["ubicacion"], data.get("observaciones"), cliente_id),
    )

    cursor.execute("DELETE FROM cliente_proyectos WHERE cliente_id=%s", (cliente_id,))
    for codigo in data.get("proyectos", []):
        cursor.execute(
            "INSERT IGNORE INTO cliente_proyectos (cliente_id, proyecto_codigo) VALUES (%s, %s)",
            (cliente_id, codigo),
        )

    conn.commit()
    cursor.close()
    conn.close()


def eliminar_cliente(cliente_id):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0


def obtener_proveedores(busqueda=None):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if busqueda:
        like = f"%{busqueda}%"
        cursor.execute(
            """
            SELECT id, nombre, telefono, tipo_productos, ruc, ubicacion, correo, observaciones
            FROM proveedores
            WHERE nombre LIKE %s OR ubicacion LIKE %s
            ORDER BY id DESC
            """,
            (like, like),
        )
    else:
        cursor.execute(
            """
            SELECT id, nombre, telefono, tipo_productos, ruc, ubicacion, correo, observaciones
            FROM proveedores
            ORDER BY id DESC
            """
        )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def obtener_proveedor_por_id(proveedor_id):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, nombre, telefono, tipo_productos, ruc, ubicacion, correo, observaciones
        FROM proveedores
        WHERE id=%s
        """,
        (proveedor_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def crear_proveedor(data):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO proveedores (nombre, telefono, tipo_productos, ruc, ubicacion, correo, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["nombre"],
            data["telefono"],
            data["tipo_productos"],
            data["ruc"],
            data["ubicacion"],
            data.get("correo"),
            data.get("observaciones"),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_proveedor(proveedor_id, data):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE proveedores
        SET nombre=%s, telefono=%s, tipo_productos=%s, ruc=%s, ubicacion=%s, correo=%s, observaciones=%s
        WHERE id=%s
        """,
        (
            data["nombre"],
            data["telefono"],
            data["tipo_productos"],
            data["ruc"],
            data["ubicacion"],
            data.get("correo"),
            data.get("observaciones"),
            proveedor_id,
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_proveedor(proveedor_id):
    inicializar_tablas_contactos()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id=%s", (proveedor_id,))
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0
