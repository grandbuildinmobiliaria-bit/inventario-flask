import os
import unicodedata
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from flask import jsonify, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename

from app.models import personal_model
from app.models.distritos_lima import DISTRITOS_LIMA
from app.utils.auth import login_required


ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def _es_imagen_permitida(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _guardar_foto(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not _es_imagen_permitida(file_storage.filename):
        raise ValueError("Formato de imagen no válido. Usa png/jpg/jpeg/webp.")

    uploads_rel = "uploads/personal"
    uploads_abs = os.path.join(current_app.static_folder, uploads_rel)
    os.makedirs(uploads_abs, exist_ok=True)

    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid4().hex}_{filename}"
    destino = os.path.join(uploads_abs, unique_name)
    file_storage.save(destino)
    return f"{uploads_rel}/{unique_name}"


def _parsear_persona_desde_form(form, foto_path=None):
    return {
        "dni": form.get("dni", "").strip(),
        "telefono": form.get("telefono", "").strip(),
        "distrito_lima": form.get("distrito_lima", "").strip(),
        "correo": form.get("correo", "").strip().lower(),
        "nombre": form.get("nombre", "").strip(),
        "cargo": form.get("cargo", "").strip(),
        "salario_base": float(form.get("salario_base", 0) or 0),
        "observaciones_tecnicas": form.get("observaciones_tecnicas", "").strip(),
        "proyecto_codigo": form.get("proyecto_codigo", "").strip() or None,
        "foto_path": foto_path,
    }


def _whatsapp_link(numero):
    if not numero:
        return None
    limpio = "".join(ch for ch in numero if ch.isdigit())
    if not limpio:
        return None
    if not limpio.startswith("51"):
        limpio = f"51{limpio}"
    return f"https://wa.me/{limpio}"


def _normalizar_distrito(valor):
    texto = (valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in texto if not unicodedata.combining(ch))


def _coordenadas_distrito(distrito):
    distritos_normalizados = {
        _normalizar_distrito(nombre): coordenadas
        for nombre, coordenadas in DISTRITOS_LIMA.items()
    }
    return distritos_normalizados.get(_normalizar_distrito(distrito))


def _serializar_salario(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    return valor


def register_personal_routes(app):


    @app.route("/mapa")
    @login_required
    def mapa_trabajadores():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede ver el mapa de trabajadores", "error")
            return redirect(url_for("home"))
        return render_template("mapa.html")

    @app.route("/api/trabajadores/mapa")
    @login_required
    def api_trabajadores_mapa():
        if session.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403

        trabajadores = []
        for persona in personal_model.obtener_personal_para_mapa():
            coordenadas = _coordenadas_distrito(persona.get("distrito_lima"))
            if not coordenadas:
                continue

            foto_path = persona.get("foto_path")
            trabajadores.append(
                {
                    "id": persona.get("id"),
                    "nombre": persona.get("nombre"),
                    "distrito": persona.get("distrito_lima"),
                    "puesto": persona.get("cargo"),
                    "edad": None,
                    "salario": _serializar_salario(persona.get("salario_base")),
                    "contacto": persona.get("telefono"),
                    "lat": coordenadas[0],
                    "lng": coordenadas[1],
                    "foto_url": url_for("static", filename=foto_path) if foto_path else None,
                    "editar_url": url_for("personal_editar", personal_id=persona.get("id")),
                }
            )

        return jsonify(trabajadores)

    @app.route("/personal")
    @login_required
    def personal_listado():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede gestionar personal", "error")
            return redirect(url_for("home"))

        busqueda = request.args.get("q", "").strip()
        personal = personal_model.obtener_personal(busqueda=busqueda)
        for p in personal:
            p["whatsapp_url"] = _whatsapp_link(p.get("telefono"))
        return render_template("personal.html", personal=personal, busqueda=busqueda)

    @app.route("/personal/nuevo", methods=["GET", "POST"])
    @login_required
    def personal_nuevo():
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede registrar personal", "error")
            return redirect(url_for("home"))

        proyectos = personal_model.listar_proyectos()

        if request.method == "POST":
            try:
                foto_path = _guardar_foto(request.files.get("foto"))
                data = _parsear_persona_desde_form(request.form, foto_path=foto_path)

                if not all([data["dni"], data["telefono"], data["distrito_lima"], data["correo"], data["nombre"], data["cargo"]]):
                    flash("⚠️ Completa todos los campos obligatorios", "warning")
                    return render_template(
                        "personal_form.html",
                        persona=data,
                        proyectos=proyectos,
                        distritos=personal_model.DISTRITOS_LIMA,
                        accion="crear",
                    )

                personal_model.crear_persona(data)
                flash("✅ Personal registrado correctamente", "success")
                return redirect(url_for("personal_listado"))
            except Exception as e:
                flash(f"❌ Error al registrar personal: {str(e)}", "error")

        return render_template(
            "personal_form.html",
            persona=None,
            proyectos=proyectos,
            distritos=personal_model.DISTRITOS_LIMA,
            accion="crear",
        )

    @app.route("/personal/editar/<int:personal_id>", methods=["GET", "POST"])
    @login_required
    def personal_editar(personal_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede editar personal", "error")
            return redirect(url_for("home"))

        persona = personal_model.obtener_persona_por_id(personal_id)
        if not persona:
            flash("❌ Registro de personal no encontrado", "error")
            return redirect(url_for("personal_listado"))

        proyectos = personal_model.listar_proyectos()

        if request.method == "POST":
            try:
                foto_path = _guardar_foto(request.files.get("foto"))
                data = _parsear_persona_desde_form(request.form, foto_path=foto_path)
                if not foto_path:
                    data.pop("foto_path", None)

                personal_model.actualizar_persona(personal_id, data)
                flash("✅ Personal actualizado", "success")
                return redirect(url_for("personal_listado"))
            except Exception as e:
                flash(f"❌ Error al actualizar: {str(e)}", "error")

        return render_template(
            "personal_form.html",
            persona=persona,
            proyectos=proyectos,
            distritos=personal_model.DISTRITOS_LIMA,
            accion="editar",
        )

    @app.route("/personal/eliminar/<int:personal_id>", methods=["POST"])
    @login_required
    def personal_eliminar(personal_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede eliminar personal", "error")
            return redirect(url_for("home"))

        eliminado = personal_model.eliminar_persona(personal_id)
        if eliminado:
            flash("🗑️ Registro eliminado", "success")
        else:
            flash("⚠️ No se encontró el registro", "warning")
        return redirect(url_for("personal_listado"))

    @app.route("/personal/asistencia/<int:personal_id>", methods=["GET", "POST"])
    @login_required
    def personal_asistencia(personal_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede gestionar asistencias", "error")
            return redirect(url_for("home"))

        persona = personal_model.obtener_persona_por_id(personal_id)
        if not persona:
            flash("❌ Registro de personal no encontrado", "error")
            return redirect(url_for("personal_listado"))

        if request.method == "POST":
            try:
                personal_model.registrar_asistencia(
                    {
                        "personal_id": personal_id,
                        "proyecto_codigo": request.form.get("proyecto_codigo", "").strip() or persona.get("proyecto_codigo"),
                        "fecha": request.form.get("fecha"),
                        "estado": request.form.get("estado", "presente"),
                        "horas_trabajadas": float(request.form.get("horas_trabajadas", 0) or 0),
                        "observaciones": request.form.get("observaciones", "").strip(),
                    }
                )
                flash("✅ Asistencia guardada", "success")
                return redirect(url_for("personal_asistencia", personal_id=personal_id))
            except Exception as e:
                flash(f"❌ Error al registrar asistencia: {str(e)}", "error")

        asistencias = personal_model.obtener_asistencias_por_persona(personal_id)
        resumen = personal_model.obtener_resumen_salario(personal_id)
        proyectos = personal_model.listar_proyectos()
        return render_template(
            "personal_asistencia.html",
            persona=persona,
            asistencias=asistencias,
            resumen=resumen,
            proyectos=proyectos,
            hoy=datetime.now().date().isoformat(),
        )

    @app.route("/personal/salarios/<int:personal_id>", methods=["GET", "POST"])
    @login_required
    def personal_salarios(personal_id):
        if session.get("rol") != "admin":
            flash("❌ Solo admin puede gestionar pagos", "error")
            return redirect(url_for("home"))

        persona = personal_model.obtener_persona_por_id(personal_id)
        if not persona:
            flash("❌ Registro de personal no encontrado", "error")
            return redirect(url_for("personal_listado"))

        if request.method == "POST":
            try:
                personal_model.registrar_pago(
                    {
                        "personal_id": personal_id,
                        "proyecto_codigo": request.form.get("proyecto_codigo", "").strip() or persona.get("proyecto_codigo"),
                        "periodo": request.form.get("periodo", "").strip(),
                        "monto": float(request.form.get("monto", 0) or 0),
                        "fecha_pago": request.form.get("fecha_pago"),
                        "observaciones": request.form.get("observaciones", "").strip(),
                    }
                )
                flash("✅ Pago registrado", "success")
                return redirect(url_for("personal_salarios", personal_id=personal_id))
            except Exception as e:
                flash(f"❌ Error al registrar pago: {str(e)}", "error")

        pagos = personal_model.obtener_pagos_por_persona(personal_id)
        resumen = personal_model.obtener_resumen_salario(personal_id)
        proyectos = personal_model.listar_proyectos()
        return render_template(
            "personal_salarios.html",
            persona=persona,
            pagos=pagos,
            resumen=resumen,
            proyectos=proyectos,
            hoy=datetime.now().date().isoformat(),
        )

    @app.route("/personal/registro-publico", methods=["GET", "POST"])
    def personal_registro_publico():
        proyectos = personal_model.listar_proyectos()

        if request.method == "POST":
            try:
                foto_path = _guardar_foto(request.files.get("foto"))
                data = _parsear_persona_desde_form(request.form, foto_path=foto_path)

                if not all([data["dni"], data["telefono"], data["distrito_lima"], data["correo"], data["nombre"], data["cargo"], data.get("foto_path")]):
                    flash("⚠️ Debes completar todos los campos y adjuntar foto", "warning")
                    return render_template(
                        "registro_personal_publico.html",
                        proyectos=proyectos,
                        distritos=personal_model.DISTRITOS_LIMA,
                    )

                personal_model.crear_persona(data)
                flash("✅ Información enviada correctamente. Gracias.", "success")
                return redirect(url_for("personal_registro_publico"))
            except Exception as e:
                flash(f"❌ No se pudo enviar la información: {str(e)}", "error")

        return render_template(
            "registro_personal_publico.html",
            proyectos=proyectos,
            distritos=personal_model.DISTRITOS_LIMA,
        )
