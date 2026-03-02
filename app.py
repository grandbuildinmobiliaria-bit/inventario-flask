from flask import Flask, session, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
import mysql.connector
import os
import qrcode
from functools import wraps
from datetime import datetime

load_dotenv()

# -------------------------
# GENERAR QR
# -------------------------
def generar_qr(codigo):
    url = f"http://localhost:5000/producto/{codigo}"
    img = qrcode.make(url)
    ruta_relativa = f"qr/{codigo}.png"
    ruta_completa = os.path.join("static", ruta_relativa)
    os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
    img.save(ruta_completa)
    return ruta_relativa

# -------------------------
# APP
# -------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
# La sesión expira al cerrar el navegador
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = 180  # opcional, en segundos (3 min)

# -------------------------
# CONEXIÓN MYSQL
# -------------------------
def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

# -------------------------
# DECORADOR LOGIN REQUIRED
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            flash("⚠️ Debes iniciar sesión primero", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
# DECORADOR ROLE REQUIRED
# -------------------------
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("rol") not in roles:
                flash("⛔ No tienes permiso para acceder aquí", "error")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s",
            (username, password)
        )
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            session["usuario"] = usuario["username"]
            session["rol"] = usuario["rol"]  # Guardamos el rol
            flash("✅ Bienvenido " + usuario["username"], "success")
            return redirect(url_for("home"))
        else:
            flash("❌ Usuario o contraseña incorrectos", "error")

    return render_template("login.html")

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("👋 Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))

# -------------------------
# HOME
# -------------------------
@app.route("/")
@login_required
def home():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # Total productos
    cursor.execute("SELECT COUNT(*) as total FROM inventario_2026_1___inventary_all")
    total_productos = cursor.fetchone()["total"]

    # Productos con stock bajo (ejemplo < 5)
    cursor.execute("SELECT COUNT(*) as bajos FROM inventario_2026_1___inventary_all WHERE STOCK < 5")
    stock_bajo = cursor.fetchone()["bajos"]

    # Solicitudes pendientes (solo admin verá el número)
    cursor.execute("SELECT COUNT(*) as total FROM solicitudes")
    solicitudes_pendientes = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "home.html",
        total_productos=total_productos,
        stock_bajo=stock_bajo,
        solicitudes_pendientes=solicitudes_pendientes
    )
# -------------------------
# LISTA PRODUCTOS (admin)
# -------------------------
@app.route("/lista_productos")
@login_required
@role_required("admin")
def lista_productos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario_2026_1___inventary_all")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("lista.html", productos=productos)

# -------------------------
# PRODUCTO
# -------------------------
@app.route("/producto/<codigo>", methods=["GET", "POST"])
@login_required
def producto(codigo):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM inventario_2026_1___inventary_all WHERE CODIGO=%s",
        (codigo,)
    )
    producto = cursor.fetchone()
    cursor.close()
    conn.close()

    if not producto:
        flash(f"❌ Producto {codigo} no encontrado", "error")
        return redirect(url_for("nuevo_producto"))

    if request.method == "POST":
        try:
            cantidad = int(request.form.get("cantidad", 0))
            ubicacion = request.form.get("ubicacion", producto.get("UBICACION"))
            stock_actual = int(producto.get("STOCK", 0))

            if cantidad <= 0:
                flash("❌ Cantidad inválida", "error")
                return redirect(url_for("producto", codigo=codigo))

            if cantidad > stock_actual:
                flash("❌ Stock insuficiente", "error")
                return redirect(url_for("producto", codigo=codigo))

            seleccionados = session.get("seleccionados", [])
            seleccionados.append({
                "CODIGO": codigo,
                "NOMBRE": producto.get("NOMBRE"),
                "cantidad": cantidad,
                "ubicacion": ubicacion,
                "QR_PATH": producto.get("QR_PATH")
            })
            session["seleccionados"] = seleccionados
            return redirect(url_for("resumen"))

        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for("producto", codigo=codigo))

    return render_template("producto.html", producto=producto)

# -------------------------
# RESUMEN
# -------------------------
@app.route("/resumen")
@login_required
def resumen():
    seleccionados = session.get("seleccionados", [])
    return render_template("resumen.html", productos=seleccionados)

# -------------------------
# ELIMINAR DEL RESUMEN
# -------------------------
@app.route("/eliminar/<codigo>")
@login_required
def eliminar(codigo):
    seleccionados = session.get("seleccionados", [])
    seleccionados = [p for p in seleccionados if p["CODIGO"] != codigo]
    session["seleccionados"] = seleccionados
    return redirect(url_for("resumen"))

# -------------------------
# CONFIRMAR ACTUALIZACIÓN
# -------------------------
@app.route("/confirmar")
@login_required
def confirmar():
    try:
        conn = conectar()
        cursor = conn.cursor()
        for p in session.get("seleccionados", []):
            cursor.execute("""
                UPDATE inventario_2026_1___inventary_all
                SET STOCK = STOCK - %s, UBICACION=%s
                WHERE CODIGO=%s
            """, (p["cantidad"], p["ubicacion"], p["CODIGO"]))
        conn.commit()
        cursor.close()
        conn.close()
        session["seleccionados"] = []
        flash("✅ Inventario actualizado correctamente", "success")
    except Exception as e:
        flash(f"❌ Error al actualizar: {str(e)}", "error")
    return redirect(url_for("resumen"))


# -------------------------
# ENVIAR SOLICUTUD AL ADMIN
# -------------------------
@app.route("/enviar_solicitud")
@login_required
def enviar_solicitud():
    if session.get("rol") != "operador":
        flash("❌ Solo operadores pueden enviar solicitudes", "error")
        return redirect(url_for("home"))

    seleccionados = session.get("seleccionados", [])
    if not seleccionados:
        flash("⚠️ No hay productos seleccionados", "warning")
        return redirect(url_for("resumen"))

    try:
        conn = conectar()
        cursor = conn.cursor()

        for p in seleccionados:
            cursor.execute("""
                INSERT INTO solicitudes (usuario, codigo_producto, nombre_producto, cantidad, ubicacion, qr_path, fecha)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session["usuario"],
                p["CODIGO"],
                p["NOMBRE"],
                p["cantidad"],
                p["ubicacion"],
                p.get("QR_PATH"),  # Agregar QR
                datetime.now()
            ))

        conn.commit()
        cursor.close()
        conn.close()

        session["seleccionados"] = []  # Limpiar resumen
        flash("✅ Solicitud enviada correctamente al admin", "success")
    except Exception as e:
        flash(f"❌ Error al enviar solicitud: {str(e)}", "error")

    return redirect(url_for("resumen"))

# -------------------------
# SOLICITUDES (solo admin)
# -------------------------
@app.route("/solicitudes")
@login_required
def solicitudes():
    if session.get("rol") != "admin":
        flash("❌ Solo admin puede ver las solicitudes", "error")
        return redirect(url_for("home"))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM solicitudes ORDER BY fecha DESC")
    solicitudes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("solicitudes.html", solicitudes=solicitudes)

# -------------------------
# APROBAR RESUMEN (solo admin)
# -------------------------
@app.route("/aprobar_todo")
@login_required
def aprobar_todo():
    if session.get("rol") != "admin":
        flash("❌ Solo admin puede aprobar solicitudes", "error")
        return redirect(url_for("home"))

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        # Obtener todas las solicitudes pendientes
        cursor.execute("SELECT * FROM solicitudes ORDER BY id ASC")
        solicitudes = cursor.fetchall()

        if not solicitudes:
            flash("⚠️ No hay solicitudes para aprobar", "warning")
            cursor.close()
            conn.close()
            return redirect(url_for("solicitudes"))

        # Actualizar stock de todos los productos
        for s in solicitudes:
            cursor.execute("""
                UPDATE inventario_2026_1___inventary_all
                SET STOCK = STOCK - %s
                WHERE CODIGO = %s
            """, (s["cantidad"], s["codigo_producto"]))

        # Guardar aprobador y fecha
        aprobador = session.get("usuario")
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Limpiar todas las solicitudes (aprobadas)
        cursor.execute("DELETE FROM solicitudes")
        conn.commit()
        cursor.close()
        conn.close()

        # Redirigir a la boleta en una ventana nueva usando query params
        return render_template("boleta.html", productos=solicitudes, aprobador=aprobador, fecha=fecha)

    except Exception as e:
        flash(f"❌ Error al aprobar solicitudes: {str(e)}", "error")
        return redirect(url_for("solicitudes"))

# -------------------------
# RECHAZAR RESUMEN (solo admin)
# -------------------------
@app.route("/rechazar/<int:id>")
@login_required
def rechazar(id):
    if session.get("rol") != "admin":
        flash("❌ Solo admin puede rechazar", "error")
        return redirect(url_for("home"))

    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM solicitudes WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash("❌ Solicitud rechazada y eliminada", "info")
    except Exception as e:
        flash(f"❌ Error al rechazar solicitud: {str(e)}", "error")

    return redirect(url_for("solicitudes"))

# -------------------------
# NUEVO (BUSCAR PRODUCTO)
# -------------------------
@app.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM familias")
    familias = cursor.fetchall()
    cursor.execute("SELECT * FROM tipos")
    tipos = cursor.fetchall()
    productos = []

    if request.method == "POST":
        familia = request.form.get("familia")
        tipo = request.form.get("tipo")
        cursor.execute("""
            SELECT CODIGO, NOMBRE 
            FROM inventario_2026_1___inventary_all
            WHERE CODIGO LIKE %s
        """, (f"{familia}-{tipo}-%",))
        productos = cursor.fetchall()
        codigo = request.form.get("producto")
        if codigo:
            cursor.close()
            conn.close()
            return redirect(url_for("producto", codigo=codigo))

    cursor.close()
    conn.close()
    return render_template("nuevo.html", familias=familias, tipos=tipos, productos=productos)

# -------------------------
# QR (INFO DEL PRODUCTO)
# -------------------------
@app.route("/producto_info/<codigo>")
@login_required
def producto_info(codigo):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT CODIGO, NOMBRE, STOCK, QR_PATH FROM inventario_2026_1___inventary_all WHERE CODIGO=%s",
            (codigo,)
        )
        producto = cursor.fetchone()
        cursor.close()
        conn.close()

        if producto:
            return producto  # Flask convierte dict a JSON automáticamente
        else:
            return {"error": "Producto no encontrado"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

# -------------------------
# CREAR PRODUCTO (admin)
# -------------------------
@app.route("/crear", methods=["GET", "POST"])
@login_required
@role_required("admin")
def crear_producto():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM familias")
    familias = cursor.fetchall()
    cursor.execute("SELECT * FROM tipos")
    tipos = cursor.fetchall()

    if request.method == "POST":
        familia = request.form.get("familia")
        tipo = request.form.get("tipo")
        cursor.execute("""
            SELECT MAX(CAST(SUBSTRING_INDEX(CODIGO, '-', -1) AS UNSIGNED)) AS ultimo
            FROM inventario_2026_1___inventary_all
            WHERE CODIGO LIKE %s
        """, (f"{familia}-{tipo}-%",))
        ultimo = cursor.fetchone()["ultimo"] or 0
        correlativo = ultimo + 1
        codigo = f"{familia}-{tipo}-{correlativo:03d}"
        nombre = request.form.get("nombre")
        stock = int(request.form.get("stock", 0))
        ubicacion = request.form.get("ubicacion")
        ruta_qr = generar_qr(codigo)
        cursor.execute("""
            INSERT INTO inventario_2026_1___inventary_all
            (CODIGO, NOMBRE, STOCK, UBICACION, QR_PATH)
            VALUES (%s, %s, %s, %s, %s)
        """, (codigo, nombre, stock, ubicacion, ruta_qr))
        conn.commit()
        flash(f"✅ Producto {codigo} creado correctamente", "success")
        return redirect(url_for("crear_producto"))

    cursor.close()
    conn.close()
    return render_template("crear.html", familias=familias, tipos=tipos)

# -------------------------
# BORRAR PRODUCTO (admin)
# -------------------------
@app.route("/borrar/<codigo>")
@login_required
@role_required("admin")
def borrar_producto(codigo):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario_2026_1___inventary_all WHERE CODIGO=%s", (codigo,))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"✅ Producto {codigo} eliminado correctamente", "success")
    except Exception as e:
        flash(f"❌ Error al eliminar producto: {str(e)}", "error")
    return redirect(url_for("lista_productos"))

# -------------------------
# CREAR USUARIO (solo admin)
# -------------------------
@app.route("/crear_usuario", methods=["GET", "POST"])
@login_required
def crear_usuario():
    if session.get("rol") != "admin":
        flash("❌ Acceso denegado", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        rol = request.form.get("rol")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)", (username, password, rol))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"✅ Usuario {username} creado", "success")
        return redirect(url_for("usuarios"))

    return render_template("crear_usuario.html")

# -------------------------
# EDITAR USUARIO (solo admin)
# -------------------------
@app.route("/editar_usuario/<int:id>", methods=["GET", "POST"])
@login_required
def editar_usuario(id):
    if session.get("rol") != "admin":
        flash("❌ Acceso denegado", "error")
        return redirect(url_for("home"))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        rol = request.form.get("rol")
        cursor.execute("UPDATE usuarios SET username=%s, password=%s, rol=%s WHERE id=%s", (username, password, rol, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"✅ Usuario actualizado", "success")
        return redirect(url_for("usuarios"))

    cursor.execute("SELECT * FROM usuarios WHERE id=%s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("editar_usuario.html", usuario=usuario)

# -------------------------
# BORRAR USUARIO (solo admin)
# -------------------------
@app.route("/borrar_usuario/<int:id>")
@login_required
def borrar_usuario(id):
    if session.get("rol") != "admin":
        flash("❌ Acceso denegado", "error")
        return redirect(url_for("home"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Usuario eliminado", "success")
    return redirect(url_for("usuarios"))

# -------------------------
# GESTIONAR USUARIOS (solo admin)
# -------------------------
@app.route("/usuarios")
@login_required
def usuarios():
    if session.get("rol") != "admin":
        flash("❌ Acceso denegado", "error")
        return redirect(url_for("home"))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, rol FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("usuarios.html", usuarios=usuarios)

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    