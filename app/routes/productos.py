from flask import session, request, render_template, redirect, url_for, flash

from app.models import producto_model
from app.services.producto_service import crear_producto_desde_form
from app.utils.auth import login_required, role_required


def register_productos_routes(app):
    @app.route("/lista_productos")
    @login_required
    @role_required("admin")
    def lista_productos():
        productos = producto_model.obtener_todos_productos()
        return render_template("lista.html", productos=productos)

    @app.route("/nuevo", methods=["GET", "POST"])
    @login_required
    def nuevo_producto():
        familias, tipos = producto_model.obtener_familias_y_tipos()
        productos = []

        if request.method == "POST":
            codigo_qr = request.form.get("codigo", "").strip()
            if codigo_qr:
                return redirect(url_for("producto", codigo=codigo_qr))

            familia = request.form.get("familia")
            tipo = request.form.get("tipo")
            productos = producto_model.buscar_productos_por_familia_tipo(familia, tipo)
            codigo = request.form.get("producto")
            if codigo:
                return redirect(url_for("producto", codigo=codigo))

        return render_template("nuevo.html", familias=familias, tipos=tipos, productos=productos)

    @app.route("/producto/<codigo>", methods=["GET", "POST"])
    @login_required
    def producto(codigo):
        producto_db = producto_model.obtener_producto_por_codigo(codigo)

        if not producto_db:
            flash(f"❌ Producto {codigo} no encontrado", "error")
            return redirect(url_for("nuevo_producto"))

        if request.method == "POST":
            try:
                cantidad = int(request.form.get("cantidad", 0))
                ubicacion = request.form.get("ubicacion", producto_db.get("UBICACION"))
                stock_actual = int(producto_db.get("STOCK", 0))

                if cantidad <= 0:
                    flash("❌ Cantidad inválida", "error")
                    return redirect(url_for("producto", codigo=codigo))

                if cantidad > stock_actual:
                    flash("❌ Stock insuficiente", "error")
                    return redirect(url_for("producto", codigo=codigo))

                seleccionados = session.get("seleccionados", [])
                seleccionados.append(
                    {
                        "CODIGO": codigo,
                        "NOMBRE": producto_db.get("NOMBRE"),
                        "cantidad": cantidad,
                        "ubicacion": ubicacion,
                        "QR_PATH": producto_db.get("QR_PATH"),
                    }
                )
                session["seleccionados"] = seleccionados
                return redirect(url_for("resumen"))
            except Exception as e:
                flash(f"❌ Error: {str(e)}", "error")
                return redirect(url_for("producto", codigo=codigo))

        return render_template("producto.html", producto=producto_db)

    @app.route("/producto_info/<codigo>")
    @login_required
    def producto_info(codigo):
        try:
            producto_db = producto_model.obtener_producto_por_codigo(codigo)
            if producto_db:
                return {
                    "CODIGO": producto_db.get("CODIGO"),
                    "NOMBRE": producto_db.get("NOMBRE"),
                    "STOCK": producto_db.get("STOCK"),
                    "QR_PATH": producto_db.get("QR_PATH"),
                }
            return {"error": "Producto no encontrado"}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    @app.route("/crear", methods=["GET", "POST"])
    @login_required
    @role_required("admin")
    def crear_producto():
        familias, tipos = producto_model.obtener_familias_y_tipos()

        if request.method == "POST":
            familia = request.form.get("familia")
            tipo = request.form.get("tipo")
            nombre = request.form.get("nombre")
            stock = int(request.form.get("stock", 0))
            ubicacion = request.form.get("ubicacion")

            codigo = crear_producto_desde_form(familia, tipo, nombre, stock, ubicacion)
            flash(f"✅ Producto {codigo} creado correctamente", "success")
            return redirect(url_for("crear_producto"))

        return render_template("crear.html", familias=familias, tipos=tipos)

    @app.route("/borrar/<codigo>")
    @login_required
    @role_required("admin")
    def borrar_producto(codigo):
        try:
            producto_model.borrar_producto(codigo)
            flash(f"✅ Producto {codigo} eliminado correctamente", "success")
        except Exception as e:
            flash(f"❌ Error al eliminar producto: {str(e)}", "error")
        return redirect(url_for("lista_productos"))
