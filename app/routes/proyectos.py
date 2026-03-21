from datetime import datetime

from flask import session, render_template, redirect, url_for, flash, request

from app.models import inventario_model, proyecto_model, contacto_model
from app.integrations.google_drive import GoogleDriveIntegration
from app.services.inventario_service import enviar_solicitud, aprobar_todas_solicitudes
from app.utils.auth import login_required


def register_proyectos_routes(app):


    @app.route("/proyectos")
    @login_required
    def proyectos():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede ver proyectos", "error")
            return redirect(url_for("home"))

        proyectos_db = proyecto_model.obtener_proyectos()
        return render_template("proyectos.html", proyectos=proyectos_db)

    @app.route("/proyectos/crear", methods=["GET", "POST"])
    @login_required
    def crear_proyecto_drive():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede crear proyectos", "error")
            return redirect(url_for("home"))

        if request.method == "POST":
            codigo = request.form.get("codigo", "").strip().upper()
            nombre = request.form.get("nombre", "").strip()
            cliente = request.form.get("cliente", "").strip()
            estado = request.form.get("estado", "activo").strip() or "activo"

            if not codigo or not nombre or not cliente:
                flash("⚠️ Debes completar código, nombre y cliente", "warning")
                return render_template("crear_proyecto.html")

            try:
                integration = GoogleDriveIntegration()
                estructura = integration.crear_y_registrar_proyecto(
                    codigo=codigo,
                    nombre=nombre,
                    cliente=cliente,
                    estado=estado,
                )
                flash(
                    f"✅ Proyecto {codigo} creado. Carpeta Drive: {estructura['root_folder_id']}",
                    "success",
                )
                return redirect(url_for("proyectos"))
            except Exception as e:
                flash(f"❌ Error al crear proyecto en Drive: {str(e)}", "error")

        return render_template("crear_proyecto.html")

    @app.route("/proyectos/editar/<codigo>", methods=["GET", "POST"])
    @login_required
    def editar_proyecto(codigo):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede editar proyectos", "error")
            return redirect(url_for("home"))

        proyecto = proyecto_model.obtener_proyecto_por_codigo(codigo)
        if not proyecto:
            flash(f"❌ No existe el proyecto {codigo}", "error")
            return redirect(url_for("proyectos"))

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            cliente = request.form.get("cliente", "").strip()
            drive_folder_id = request.form.get("drive_folder_id", "").strip()
            estado = request.form.get("estado", "activo").strip() or "activo"

            if not nombre or not cliente or not drive_folder_id:
                flash("⚠️ Debes completar nombre, cliente y drive_folder_id", "warning")
                proyecto = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "cliente": cliente,
                    "drive_folder_id": drive_folder_id,
                    "estado": estado,
                }
                return render_template("editar_proyecto.html", proyecto=proyecto)

            actualizado = proyecto_model.actualizar_proyecto(
                codigo=codigo,
                nombre=nombre,
                cliente=cliente,
                drive_folder_id=drive_folder_id,
                estado=estado,
            )
            if actualizado:
                flash(f"✅ Proyecto {codigo} actualizado correctamente", "success")
            else:
                flash(f"⚠️ No se pudo actualizar el proyecto {codigo}", "warning")
            return redirect(url_for("proyectos"))

        return render_template("editar_proyecto.html", proyecto=proyecto)

    @app.route("/proyectos/eliminar/<codigo>", methods=["POST"])
    @login_required
    def eliminar_proyecto(codigo):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede eliminar proyectos", "error")
            return redirect(url_for("home"))

        eliminado = proyecto_model.eliminar_proyecto_por_codigo(codigo)
        if eliminado:
            flash(f"🗑️ Proyecto {codigo} eliminado correctamente", "success")
        else:
            flash(f"⚠️ No existe el proyecto {codigo}", "warning")
        return redirect(url_for("proyectos"))

    @app.route("/proyectos/abrir/<codigo>")
    @login_required
    def abrir_proyecto_drive(codigo):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede abrir carpetas de proyectos", "error")
            return redirect(url_for("home"))

        proyecto = proyecto_model.obtener_proyecto_por_codigo(codigo)
        if not proyecto or not proyecto.get("drive_folder_id"):
            flash(f"⚠️ El proyecto {codigo} no tiene carpeta de Drive registrada", "warning")
            return redirect(url_for("proyectos"))

        drive_url = f"https://drive.google.com/drive/folders/{proyecto['drive_folder_id']}"
        return redirect(drive_url)

    @app.route("/proyectos/agregar-cliente/<codigo>", methods=["GET", "POST"])
    @login_required
    def agregar_cliente_proyecto(codigo):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede asociar clientes a proyectos", "error")
            return redirect(url_for("home"))

        proyecto = proyecto_model.obtener_proyecto_por_codigo(codigo)
        if not proyecto:
            flash(f"❌ No existe el proyecto {codigo}", "error")
            return redirect(url_for("proyectos"))

        clientes = contacto_model.obtener_clientes()
        if request.method == "POST":
            cliente_nombre = request.form.get("cliente", "").strip()
            if not cliente_nombre:
                flash("⚠️ Debes seleccionar un cliente", "warning")
                return render_template(
                    "asignar_cliente_proyecto.html",
                    proyecto=proyecto,
                    clientes=clientes,
                )

            actualizado = proyecto_model.actualizar_proyecto(
                codigo=codigo,
                nombre=proyecto["nombre"],
                cliente=cliente_nombre,
                drive_folder_id=proyecto["drive_folder_id"],
                estado=proyecto["estado"],
            )
            if actualizado:
                flash(f"✅ Cliente asignado al proyecto {codigo}", "success")
            else:
                flash(f"⚠️ No se pudo asignar cliente al proyecto {codigo}", "warning")
            return redirect(url_for("proyectos"))

        return render_template(
            "asignar_cliente_proyecto.html",
            proyecto=proyecto,
            clientes=clientes,
        )

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
        if not session.get("proyecto_codigo"):
            flash("⚠️ Debes seleccionar un proyecto antes de enviar solicitud", "warning")
            return redirect(url_for("nuevo_producto"))

        try:
            enviar_solicitud(session["usuario"], seleccionados)
            session["seleccionados"] = []
            flash("✅ Solicitud enviada correctamente al admin", "success")
        except Exception as e:
            flash(f"❌ Error al enviar solicitud: {str(e)}", "error")

        return redirect(url_for("resumen"))

    @app.route("/mis_solicitudes")
    @login_required
    def mis_solicitudes():
        if session.get("rol") != "operador":
            flash("❌ Solo operadores pueden ver su historial", "error")
            return redirect(url_for("home"))

        data = inventario_model.obtener_historial_solicitudes_por_usuario(session["usuario"])
        return render_template("mis_solicitudes.html", solicitudes=data)

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
