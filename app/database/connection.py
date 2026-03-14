import mysql.connector
from flask import current_app


def conectar():
    return mysql.connector.connect(
        host=current_app.config.get("DB_HOST"),
        user=current_app.config.get("DB_USER"),
        password=current_app.config.get("DB_PASS"),
        database=current_app.config.get("DB_NAME"),
    )
