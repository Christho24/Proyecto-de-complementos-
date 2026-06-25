import json
import os
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:18000/")
MONGO_DB = os.getenv("MONGO_DB", "finis_trabaja")
ARCHIVO_DATOS = Path(__file__).with_name("datos_demo.json")


def cargar():
    datos = json.loads(ARCHIVO_DATOS.read_text(encoding="utf-8"))
    cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    cliente.admin.command("ping")
    db = cliente[MONGO_DB]
    ahora = datetime.now(timezone.utc)

    for usuario in datos["usuarios"]:
        db["Usuarios"].update_one(
            {"id_usuario": usuario["id_usuario"]},
            {"$set": usuario},
            upsert=True,
        )

    perfil = datos["perfil_cvv"]
    db["PerfilCVV"].update_one(
        {"estudiante_id": perfil["estudiante_id"]},
        {"$set": perfil},
        upsert=True,
    )

    for oferta in datos["ofertas"]:
        documento = {
            **oferta,
            "empresa_id": datos["empresa_id"],
            "estado": "habilitada",
            "fecha_publicacion": ahora,
        }
        db["Ofertas"].update_one(
            {"codigo_demo": oferta["codigo_demo"]},
            {"$set": documento},
            upsert=True,
        )

    print(
        "Datos demo cargados: "
        f"{len(datos['usuarios'])} usuarios, 1 PerfilCVV y "
        f"{len(datos['ofertas'])} ofertas."
    )


if __name__ == "__main__":
    cargar()
