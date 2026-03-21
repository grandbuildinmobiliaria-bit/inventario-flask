from dotenv import load_dotenv
from flask import Flask

from config import Config
from app.routes.productos import register_productos_routes
from app.routes.inventario import register_inventario_routes
from app.routes.proyectos import register_proyectos_routes
from app.routes.personal import register_personal_routes


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    register_productos_routes(app)
    register_inventario_routes(app)
    register_proyectos_routes(app)
    register_personal_routes(app)

    return app
