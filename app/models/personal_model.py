from app.database.connection import conectar


DISTRITOS_LIMA = [
    "Ancón", "Ate", "Barranco", "Breña", "Carabayllo", "Chaclacayo", "Chorrillos",
    "Cieneguilla", "Comas", "El Agustino", "Independencia", "Jesús María", "La Molina",
    "La Victoria", "Lima", "Lince", "Los Olivos", "Lurigancho", "Lurín",
    "Magdalena del Mar", "Miraflores", "Pachacámac", "Pucusana", "Pueblo Libre",
    "Puente Piedra", "Punta Hermosa", "Punta Negra", "Rímac", "San Bartolo",
    "San Borja", "San Isidro", "San Juan de Lurigancho", "San Juan de Miraflores",
    "San Luis", "San Martín de Porres", "San Miguel", "Santa Anita", "Santa María del Mar",
    "Santa Rosa", "Santiago de Surco", "Surquillo", "Villa El Salvador", "Villa María del Triunfo",
]


def inicializar_tablas_personal():
    """Crea tablas mínimas para gestión de personal/asistencia/salarios si no existen."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS personal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dni VARCHAR(16) NOT NULL UNIQUE,
            telefono VARCHAR(30) NOT NULL,
            distrito_lima VARCHAR(80) NOT NULL,
            correo VARCHAR(120) NOT NULL,
            nombre VARCHAR(120) NOT NULL,
            cargo VARCHAR(120) NOT NULL,
            salario_base DECIMAL(10,2) NOT NULL DEFAULT 0,
            observaciones_tecnicas TEXT,
            proyecto_codigo VARCHAR(50),
            foto_path VARCHAR(255),
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS asistencias_personal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            personal_id INT NOT NULL,
            proyecto_codigo VARCHAR(50),
            fecha DATE NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'presente',
            horas_trabajadas DECIMAL(5,2) NOT NULL DEFAULT 0,
            observaciones VARCHAR(255),
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_asistencia_persona_fecha (personal_id, fecha),
            CONSTRAINT fk_asistencia_personal FOREIGN KEY (personal_id)
                REFERENCES personal(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pagos_personal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            personal_id INT NOT NULL,
            proyecto_codigo VARCHAR(50),
            periodo VARCHAR(20) NOT NULL,
            monto DECIMAL(10,2) NOT NULL,
            fecha_pago DATE NOT NULL,
            observaciones VARCHAR(255),
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_pago_personal FOREIGN KEY (personal_id)
                REFERENCES personal(id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


def obtener_personal():
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, dni, telefono, distrito_lima, correo, nombre, cargo,
               salario_base, observaciones_tecnicas, proyecto_codigo, foto_path
        FROM personal
        ORDER BY id DESC
        """
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def obtener_persona_por_id(personal_id):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, dni, telefono, distrito_lima, correo, nombre, cargo,
               salario_base, observaciones_tecnicas, proyecto_codigo, foto_path
        FROM personal
        WHERE id=%s
        """,
        (personal_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def crear_persona(data):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO personal
            (dni, telefono, distrito_lima, correo, nombre, cargo, salario_base,
             observaciones_tecnicas, proyecto_codigo, foto_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["dni"],
            data["telefono"],
            data["distrito_lima"],
            data["correo"],
            data["nombre"],
            data["cargo"],
            data["salario_base"],
            data.get("observaciones_tecnicas"),
            data.get("proyecto_codigo"),
            data.get("foto_path"),
        ),
    )
    conn.commit()
    created = cursor.lastrowid
    cursor.close()
    conn.close()
    return created


def actualizar_persona(personal_id, data):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor()

    base_sql = """
        UPDATE personal
        SET dni=%s, telefono=%s, distrito_lima=%s, correo=%s, nombre=%s,
            cargo=%s, salario_base=%s, observaciones_tecnicas=%s, proyecto_codigo=%s
    """
    params = [
        data["dni"],
        data["telefono"],
        data["distrito_lima"],
        data["correo"],
        data["nombre"],
        data["cargo"],
        data["salario_base"],
        data.get("observaciones_tecnicas"),
        data.get("proyecto_codigo"),
    ]

    if data.get("foto_path"):
        base_sql += ", foto_path=%s"
        params.append(data["foto_path"])

    base_sql += " WHERE id=%s"
    params.append(personal_id)

    cursor.execute(base_sql, tuple(params))
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0


def eliminar_persona(personal_id):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personal WHERE id=%s", (personal_id,))
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0


def listar_proyectos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT codigo, nombre FROM proyectos ORDER BY codigo ASC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def registrar_asistencia(data):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO asistencias_personal (personal_id, proyecto_codigo, fecha, estado, horas_trabajadas, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            proyecto_codigo=VALUES(proyecto_codigo),
            estado=VALUES(estado),
            horas_trabajadas=VALUES(horas_trabajadas),
            observaciones=VALUES(observaciones)
        """,
        (
            data["personal_id"],
            data.get("proyecto_codigo"),
            data["fecha"],
            data["estado"],
            data["horas_trabajadas"],
            data.get("observaciones"),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_asistencias_por_persona(personal_id):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, personal_id, proyecto_codigo, fecha, estado, horas_trabajadas, observaciones
        FROM asistencias_personal
        WHERE personal_id=%s
        ORDER BY fecha DESC
        """,
        (personal_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def obtener_resumen_salario(personal_id):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT salario_base FROM personal WHERE id=%s", (personal_id,))
    persona = cursor.fetchone() or {"salario_base": 0}

    cursor.execute(
        """
        SELECT COALESCE(SUM(horas_trabajadas), 0) AS horas_total
        FROM asistencias_personal
        WHERE personal_id=%s AND estado='presente'
        """,
        (personal_id,),
    )
    horas = cursor.fetchone()["horas_total"]

    cursor.execute(
        """
        SELECT COALESCE(SUM(monto), 0) AS pagado
        FROM pagos_personal
        WHERE personal_id=%s
        """,
        (personal_id,),
    )
    pagado = cursor.fetchone()["pagado"]

    cursor.close()
    conn.close()

    salario_base = float(persona["salario_base"] or 0)
    horas_total = float(horas or 0)
    salario_hora = salario_base / 240 if salario_base else 0
    devengado = salario_hora * horas_total
    pendiente = devengado - float(pagado or 0)

    return {
        "salario_base": salario_base,
        "salario_hora": salario_hora,
        "horas_total": horas_total,
        "devengado": devengado,
        "pagado": float(pagado or 0),
        "pendiente": pendiente,
    }


def registrar_pago(data):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pagos_personal (personal_id, proyecto_codigo, periodo, monto, fecha_pago, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            data["personal_id"],
            data.get("proyecto_codigo"),
            data["periodo"],
            data["monto"],
            data["fecha_pago"],
            data.get("observaciones"),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_pagos_por_persona(personal_id):
    inicializar_tablas_personal()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, personal_id, proyecto_codigo, periodo, monto, fecha_pago, observaciones
        FROM pagos_personal
        WHERE personal_id=%s
        ORDER BY fecha_pago DESC, id DESC
        """,
        (personal_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
