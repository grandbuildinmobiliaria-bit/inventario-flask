from flask import session, request, render_template, redirect, url_for, flash, jsonify

from app.models import inventario_model
from app.database.connection import conectar
from app.utils.auth import login_required


def register_inventario_routes(app):

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/health/db", methods=["GET"])
    def health_db():
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return jsonify({"status": "ok", "database": "up"}), 200
        except Exception as exc:
            return jsonify({"status": "error", "database": "down", "detail": str(exc)}), 503

    @app.route("/")
    @login_required
    def home():
        total_productos, stock_bajo, solicitudes_pendientes = inventario_model.obtener_resumen_home()
        return render_template(
            "home.html",
            total_productos=total_productos,
            stock_bajo=stock_bajo,
            solicitudes_pendientes=solicitudes_pendientes,
        )

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
                (username, password),
            )
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()

            if usuario:
                session["usuario"] = usuario["username"]
                session["rol"] = usuario["rol"]
                flash("✅ Bienvenido " + usuario["username"], "success")
                return redirect(url_for("home"))

            flash("❌ Usuario o contraseña incorrectos", "error")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.clear()
        flash("👋 Sesión cerrada correctamente", "info")
        return redirect(url_for("login"))

    @app.route("/resumen")
    @login_required
    def resumen():
        seleccionados = session.get("seleccionados", [])
        return render_template("resumen.html", productos=seleccionados)

    @app.route("/eliminar/<codigo>")
    @login_required
    def eliminar(codigo):
        seleccionados = session.get("seleccionados", [])
        seleccionados = [p for p in seleccionados if p["CODIGO"] != codigo]
        session["seleccionados"] = seleccionados
        return redirect(url_for("resumen"))

    @app.route("/confirmar")
    @login_required
    def confirmar():
        try:
            inventario_model.confirmar_salida_productos(session.get("seleccionados", []))
            session["seleccionados"] = []
            flash("✅ Inventario actualizado correctamente", "success")
        except Exception as e:
            flash(f"❌ Error al actualizar: {str(e)}", "error")
        return redirect(url_for("resumen"))

    @app.route("/usuarios")
    @login_required
    def usuarios():
        if session.get("rol") != "admin":
            flash("❌ Acceso denegado", "error")
            return redirect(url_for("home"))

        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, rol FROM usuarios")
        usuarios_db = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("usuarios.html", usuarios=usuarios_db)

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
            cursor.execute(
                "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)",
                (username, password, rol),
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"✅ Usuario {username} creado", "success")
            return redirect(url_for("usuarios"))

        return render_template("crear_usuario.html")

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
            cursor.execute(
                "UPDATE usuarios SET username=%s, password=%s, rol=%s WHERE id=%s",
                (username, password, rol, id),
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("✅ Usuario actualizado", "success")
            return redirect(url_for("usuarios"))

        cursor.execute("SELECT * FROM usuarios WHERE id=%s", (id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template("editar_usuario.html", usuario=usuario)

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
