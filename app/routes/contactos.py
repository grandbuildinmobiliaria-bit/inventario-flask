from flask import render_template, request, redirect, url_for, flash, session

from app.models import contacto_model
from app.utils.auth import login_required


def _whatsapp_link(numero):
    if not numero:
        return None
    limpio = "".join(ch for ch in numero if ch.isdigit())
    if not limpio:
        return None
    if not limpio.startswith("51"):
        limpio = f"51{limpio}"
    return f"https://wa.me/{limpio}"


def _payload_cliente(form):
    return {
        "nombre": form.get("nombre", "").strip(),
        "telefono": form.get("telefono", "").strip(),
        "correo": form.get("correo", "").strip().lower(),
        "ubicacion": form.get("ubicacion", "").strip(),
        "observaciones": form.get("observaciones", "").strip(),
        "proyectos": form.getlist("proyectos"),
    }


def _payload_proveedor(form):
    return {
        "nombre": form.get("nombre", "").strip(),
        "telefono": form.get("telefono", "").strip(),
        "tipo_productos": form.get("tipo_productos", "").strip(),
        "ruc": form.get("ruc", "").strip(),
        "ubicacion": form.get("ubicacion", "").strip(),
        "correo": form.get("correo", "").strip().lower(),
        "observaciones": form.get("observaciones", "").strip(),
    }


def register_contactos_routes(app):

    @app.route("/clientes")
    @login_required
    def clientes_listado():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede gestionar clientes", "error")
            return redirect(url_for("home"))

        busqueda = request.args.get("q", "").strip()
        clientes = contacto_model.obtener_clientes(busqueda=busqueda)
        for c in clientes:
            c["whatsapp_url"] = _whatsapp_link(c.get("telefono"))
        return render_template("clientes.html", clientes=clientes, busqueda=busqueda)

    @app.route("/clientes/nuevo", methods=["GET", "POST"])
    @login_required
    def clientes_nuevo():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede crear clientes", "error")
            return redirect(url_for("home"))

        proyectos = contacto_model.obtener_proyectos_disponibles()
        if request.method == "POST":
            data = _payload_cliente(request.form)
            if not all([data["nombre"], data["telefono"], data["ubicacion"]]):
                flash("⚠️ Nombre, teléfono y ubicación son obligatorios", "warning")
                return render_template("cliente_form.html", cliente=data, proyectos=proyectos, accion="crear")

            try:
                contacto_model.crear_cliente(data)
                flash("✅ Cliente creado", "success")
                return redirect(url_for("clientes_listado"))
            except Exception as e:
                flash(f"❌ Error al crear cliente: {str(e)}", "error")

        return render_template("cliente_form.html", cliente=None, proyectos=proyectos, accion="crear")

    @app.route("/clientes/editar/<int:cliente_id>", methods=["GET", "POST"])
    @login_required
    def clientes_editar(cliente_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede editar clientes", "error")
            return redirect(url_for("home"))

        cliente = contacto_model.obtener_cliente_por_id(cliente_id)
        if not cliente:
            flash("❌ Cliente no encontrado", "error")
            return redirect(url_for("clientes_listado"))

        proyectos = contacto_model.obtener_proyectos_disponibles()
        if request.method == "POST":
            data = _payload_cliente(request.form)
            try:
                contacto_model.actualizar_cliente(cliente_id, data)
                flash("✅ Cliente actualizado", "success")
                return redirect(url_for("clientes_listado"))
            except Exception as e:
                flash(f"❌ Error al actualizar cliente: {str(e)}", "error")

        return render_template("cliente_form.html", cliente=cliente, proyectos=proyectos, accion="editar")

    @app.route("/clientes/eliminar/<int:cliente_id>", methods=["POST"])
    @login_required
    def clientes_eliminar(cliente_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede eliminar clientes", "error")
            return redirect(url_for("home"))

        eliminado = contacto_model.eliminar_cliente(cliente_id)
        if eliminado:
            flash("🗑️ Cliente eliminado", "success")
        else:
            flash("⚠️ Cliente no encontrado", "warning")
        return redirect(url_for("clientes_listado"))

    @app.route("/proveedores")
    @login_required
    def proveedores_listado():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede gestionar proveedores", "error")
            return redirect(url_for("home"))

        busqueda = request.args.get("q", "").strip()
        proveedores = contacto_model.obtener_proveedores(busqueda=busqueda)
        for p in proveedores:
            p["whatsapp_url"] = _whatsapp_link(p.get("telefono"))
        return render_template("proveedores.html", proveedores=proveedores, busqueda=busqueda)

    @app.route("/proveedores/nuevo", methods=["GET", "POST"])
    @login_required
    def proveedores_nuevo():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede crear proveedores", "error")
            return redirect(url_for("home"))

        if request.method == "POST":
            data = _payload_proveedor(request.form)
            if not all([data["nombre"], data["telefono"], data["tipo_productos"], data["ruc"], data["ubicacion"]]):
                flash("⚠️ Completa todos los campos obligatorios", "warning")
                return render_template("proveedor_form.html", proveedor=data, accion="crear")

            try:
                contacto_model.crear_proveedor(data)
                flash("✅ Proveedor creado", "success")
                return redirect(url_for("proveedores_listado"))
            except Exception as e:
                flash(f"❌ Error al crear proveedor: {str(e)}", "error")

        return render_template("proveedor_form.html", proveedor=None, accion="crear")

    @app.route("/proveedores/editar/<int:proveedor_id>", methods=["GET", "POST"])
    @login_required
    def proveedores_editar(proveedor_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede editar proveedores", "error")
            return redirect(url_for("home"))

        proveedor = contacto_model.obtener_proveedor_por_id(proveedor_id)
        if not proveedor:
            flash("❌ Proveedor no encontrado", "error")
            return redirect(url_for("proveedores_listado"))

        if request.method == "POST":
            data = _payload_proveedor(request.form)
            try:
                contacto_model.actualizar_proveedor(proveedor_id, data)
                flash("✅ Proveedor actualizado", "success")
                return redirect(url_for("proveedores_listado"))
            except Exception as e:
                flash(f"❌ Error al actualizar proveedor: {str(e)}", "error")

        return render_template("proveedor_form.html", proveedor=proveedor, accion="editar")

    @app.route("/proveedores/eliminar/<int:proveedor_id>", methods=["POST"])
    @login_required
    def proveedores_eliminar(proveedor_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede eliminar proveedores", "error")
            return redirect(url_for("home"))

        eliminado = contacto_model.eliminar_proveedor(proveedor_id)
        if eliminado:
            flash("🗑️ Proveedor eliminado", "success")
        else:
            flash("⚠️ Proveedor no encontrado", "warning")
        return redirect(url_for("proveedores_listado"))
