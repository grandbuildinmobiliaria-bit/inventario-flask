from flask import Flask, session, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
import mysql.connector
import os
import qrcode
load_dotenv()

def generar_qr(codigo):
    url = f"http://localhost:5000/producto/{codigo}"
    img = qrcode.make(url)
    ruta_relativa = f"qr/{codigo}.png"
    ruta_completa = os.path.join("static", ruta_relativa)
    os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
    img.save(ruta_completa)
    return ruta_relativa

app = Flask(__name__)
app.secret_key = "clave_super_segura_123456789!@#"  # clave robusta

# Conexión a MySQL en cPanel
def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/lista_productos")
def lista_productos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario_2026_1___inventary_all")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("lista.html", productos=productos)

@app.route("/producto/<codigo>", methods=["GET", "POST"])
def producto(codigo):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM inventario_2026_1___inventary_all WHERE CODIGO=%s",
            (codigo,)
        )
        producto = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"❌ Error de conexión: {str(e)}", "error")
        return redirect(url_for("home"))

    if not producto:
        flash(f"❌ Producto {codigo} no encontrado", "error")
        return redirect(url_for("nuevo_producto"))

    if request.method == "POST":
        try:
            cantidad = int(request.form.get("cantidad", 0))
            ubicacion = request.form.get("ubicacion", producto.get("UBICACION", "Sin ubicación"))
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
                "NOMBRE": producto.get("NOMBRE", "Sin nombre"),
                "cantidad": cantidad,
                "ubicacion": ubicacion,
                "QR_PATH": producto.get("QR_PATH", "")
            })
            session["seleccionados"] = seleccionados

            return redirect(url_for("resumen"))
        except Exception as e:
            flash(f"❌ Error al procesar: {str(e)}", "error")
            return redirect(url_for("producto", codigo=codigo))

    return render_template("producto.html", producto=producto)

@app.route("/resumen")
def resumen():
    seleccionados = session.get("seleccionados", [])
    return render_template("resumen.html", productos=seleccionados)

@app.route("/eliminar/<codigo>")
def eliminar(codigo):
    seleccionados = session.get("seleccionados", [])
    seleccionados = [p for p in seleccionados if p["CODIGO"] != codigo]
    session["seleccionados"] = seleccionados
    return redirect(url_for("resumen"))

@app.route("/confirmar")
def confirmar():
    try:
        conn = conectar()
        cursor = conn.cursor()
        for p in session.get("seleccionados", []):
            sql = """
                UPDATE inventario_2026_1___inventary_all
                SET STOCK = STOCK - %s, UBICACION=%s
                WHERE CODIGO=%s
            """
            cursor.execute(sql, (p["cantidad"], p["ubicacion"], p["CODIGO"]))
        conn.commit()
        cursor.close()
        conn.close()
        session["seleccionados"] = []
        flash("✅ Inventario actualizado correctamente", "success")
        return redirect(url_for("resumen"))
    except Exception as e:
        flash(f"❌ Error al actualizar: {str(e)}", "error")
        return redirect(url_for("resumen"))

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # Cargar familias y tipos
    cursor.execute("SELECT * FROM familias")
    familias = cursor.fetchall()
    cursor.execute("SELECT * FROM tipos")
    tipos = cursor.fetchall()

    productos = []

    if request.method == "POST":
        familia = request.form.get("familia")
        tipo = request.form.get("tipo")

        # Buscar productos que coincidan
        cursor.execute("""
            SELECT CODIGO, NOMBRE 
            FROM inventario_2026_1___inventary_all
            WHERE CODIGO LIKE %s
        """, (f"{familia}-{tipo}-%",))
        productos = cursor.fetchall()

        # Si el usuario ya seleccionó un producto
        codigo = request.form.get("producto")
        if codigo:
            cursor.close()
            conn.close()
            return redirect(url_for("producto", codigo=codigo))

    cursor.close()
    conn.close()
    return render_template("nuevo.html", familias=familias, tipos=tipos, productos=productos)

@app.route("/crear", methods=["GET", "POST"])
def crear_producto():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # Cargar familias y tipos para desplegable
    cursor.execute("SELECT * FROM familias")
    familias = cursor.fetchall()
    cursor.execute("SELECT * FROM tipos")
    tipos = cursor.fetchall()

    if request.method == "POST":
        familia = request.form.get("familia")
        tipo = request.form.get("tipo")

        # Buscar último correlativo
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

        # Generar QR
        ruta_qr = generar_qr(codigo)

        sql = """
            INSERT INTO inventario_2026_1___inventary_all
            (CODIGO, NOMBRE, STOCK, UBICACION, QR_PATH)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (codigo, nombre, stock, ubicacion, ruta_qr))
        conn.commit()

        flash(f"✅ Producto {codigo} creado correctamente", "success")
        return redirect(url_for("crear_producto"))

    cursor.close()
    conn.close()
    return render_template("crear.html", familias=familias, tipos=tipos)

@app.route("/borrar/<codigo>")
def borrar_producto(codigo):
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "DELETE FROM inventario_2026_1___inventary_all WHERE CODIGO=%s"
        cursor.execute(sql, (codigo,))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"✅ Producto {codigo} eliminado correctamente", "success")
        return redirect(url_for("lista_productos"))
    except Exception as e:
        flash(f"❌ Error al eliminar producto: {str(e)}", "error")
        return redirect(url_for("lista_productos"))

if __name__ == "__main__":
    app.run(debug=False)