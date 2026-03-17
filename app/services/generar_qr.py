import mysql.connector
import qrcode
import os

def conectar():
    return mysql.connector.connect(
        host="208.91.198.8",
        user="grand744_samuel_user",
        password="j8]]b!Xwhv}l",
        database="grand744_inventario_db"
    )

CARPETA_QR = os.path.join("static", "qr")
os.makedirs(CARPETA_QR, exist_ok=True)

def generar_qr_para_todos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT CODIGO FROM inventario_2026_1___inventary_all")
    productos = cursor.fetchall()

    for producto in productos:
        codigo = producto["CODIGO"]
        url = f"http://localhost:5000/producto/{codigo}"
        img = qrcode.make(url)

        ruta_relativa = f"qr/{codigo}.png"
        ruta_completa = os.path.join(CARPETA_QR, f"{codigo}.png")
        img.save(ruta_completa)

        # Actualizar BD con la ruta del QR
        sql = "UPDATE inventario_2026_1___inventary_all SET QR_PATH=%s WHERE CODIGO=%s"
        cursor.execute(sql, (ruta_relativa, codigo))
        print(f"✅ QR generado y guardado en BD: {codigo}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    generar_qr_para_todos()