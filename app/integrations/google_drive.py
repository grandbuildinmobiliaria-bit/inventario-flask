import os
from typing import Optional

from flask import current_app

from app.models.proyecto_model import guardar_drive_folder_id


SCOPES = ["https://www.googleapis.com/auth/drive"]
DEFAULT_SUBCARPETAS = ["Planos", "Compras", "Guías", "Evidencias", "Cierre"]


class GoogleDriveIntegration:
    """Integración base con Google Drive para estructura de carpetas por proyecto."""

    def __init__(self):
        self.service_account_file = current_app.config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
        self.parent_folder_id = current_app.config.get("GOOGLE_DRIVE_PARENT_FOLDER_ID")

    def _build_service(self):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Faltan dependencias de Google Drive. Instala requirements.txt para usar esta integración."
            ) from exc

        if not self.service_account_file:
            raise ValueError("Falta GOOGLE_SERVICE_ACCOUNT_FILE en la configuración.")

        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(f"No existe el archivo de credenciales: {self.service_account_file}")

        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=SCOPES,
        )
        return build("drive", "v3", credentials=credentials)

    def _create_folder(self, service, name: str, parent_id: Optional[str] = None) -> str:
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        folder = service.files().create(body=metadata, fields="id, name").execute()
        return folder["id"]

    def crear_estructura_proyecto(self, codigo: str, nombre: str, cliente: str):
        """
        Crea carpeta raíz por cliente/proyecto + subcarpetas automáticas.

        Resultado:
        {
            "root_folder_id": "...",
            "subfolders": {"Planos": "...", ...}
        }
        """
        service = self._build_service()

        nombre_raiz = f"{cliente} - {codigo} - {nombre}"
        root_folder_id = self._create_folder(service, nombre_raiz, self.parent_folder_id)

        subfolders = {}
        for sub in DEFAULT_SUBCARPETAS:
            subfolders[sub] = self._create_folder(service, sub, root_folder_id)

        return {"root_folder_id": root_folder_id, "subfolders": subfolders}

    def crear_y_registrar_proyecto(self, codigo: str, nombre: str, cliente: str, estado: str = "activo"):
        """Crea carpetas en Drive y guarda drive_folder_id en la tabla proyectos."""
        estructura = self.crear_estructura_proyecto(codigo=codigo, nombre=nombre, cliente=cliente)

        guardar_drive_folder_id(
            codigo=codigo,
            nombre=nombre,
            cliente=cliente,
            drive_folder_id=estructura["root_folder_id"],
            estado=estado,
        )

        return estructura
