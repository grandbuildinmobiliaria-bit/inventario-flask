from datetime import datetime

from flask import session, render_template, redirect, url_for, flash

from app.models import inventario_model
from app.services.inventario_service import enviar_solicitud, aprobar_todas_solicitudes
from app.utils.auth import login_required


def register_proyectos_routes(app):
    @app.route("/enviar_solicitud")
    @login_required
    def enviar_solicitud_route():
        if session.get("rol") != "operador":
            flash("❌ Solo operadores pueden enviar solicitudes", "error")
            return redirect(url_for("home"))

        seleccionados = session.get("seleccionados", [])
        if not seleccionados:
            flash("⚠️ No hay productos seleccionados", "warning")
            return redirect(url_for("resumen"))

        try:
            enviar_solicitud(session["usuario"], seleccionados)
            session["seleccionados"] = []
            flash("✅ Solicitud enviada correctamente al admin", "success")
        except Exception as e:
            flash(f"❌ Error al enviar solicitud: {str(e)}", "error")

        return redirect(url_for("resumen"))

    @app.route("/solicitudes")
    @login_required
    def solicitudes():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede ver las solicitudes", "error")
            return redirect(url_for("home"))

        solicitudes_db = inventario_model.obtener_solicitudes()
        return render_template("solicitudes.html", solicitudes=solicitudes_db)

    @app.route("/aprobar_todo")
    @login_required
    def aprobar_todo():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede aprobar solicitudes", "error")
            return redirect(url_for("home"))

        try:
            solicitudes_db = aprobar_todas_solicitudes()
            if not solicitudes_db:
                flash("⚠️ No hay solicitudes para aprobar", "warning")
                return redirect(url_for("solicitudes"))

            aprobador = session.get("usuario")
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            return render_template("boleta.html", productos=solicitudes_db, aprobador=aprobador, fecha=fecha)
        except Exception as e:
            flash(f"❌ Error al aprobar solicitudes: {str(e)}", "error")
            return redirect(url_for("solicitudes"))

    @app.route("/rechazar/<int:id>")
    @login_required
    def rechazar(id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede rechazar", "error")
            return redirect(url_for("home"))

        try:
            inventario_model.rechazar_solicitud(id)
            flash("❌ Solicitud rechazada y eliminada", "info")
        except Exception as e:
            flash(f"❌ Error al rechazar solicitud: {str(e)}", "error")

        return redirect(url_for("solicitudes"))
