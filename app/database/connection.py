import mysql.connector
from flask import current_app

#PARA ESCRITORIO
from dotenv import load_dotenv
import os

load_dotenv() # <--- IMPORTANTE: Sin esto, os.getenv siempre será None



def conectar():
    return mysql.connector.connect(
        host=current_app.config.get("DB_HOST"),
        user=current_app.config.get("DB_USER"),
        password=current_app.config.get("DB_PASS"),
        database=current_app.config.get("DB_NAME"),
    )
