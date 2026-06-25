from bson import ObjectId
from gridfs import GridFS
from gridfs.errors import NoFile
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import DuplicateKeyError


class ControladorBaseDatos:
    """Único punto de acceso a MongoDB, según la arquitectura planificada."""

    def __init__(self, uri, nombre_base_datos):
        self.cliente = MongoClient(uri, serverSelectionTimeoutMS=3000)
        self.db = self.cliente[nombre_base_datos]
        self.ofertas = self.db["Ofertas"]
        self.postulaciones = self.db["Postulaciones"]
        self.usuarios = self.db["Usuarios"]
        self.perfiles_cvv = self.db["PerfilCVV"]
        self.archivos = GridFS(self.db, collection="Curriculums")
        self._crear_indices()

    def _crear_indices(self):
        self.ofertas.create_index(
            [("empresa_id", ASCENDING), ("estado", ASCENDING)]
        )
        self.postulaciones.create_index(
            [("oferta_id", ASCENDING), ("estudiante_id", ASCENDING)],
            unique=True,
        )
        self.usuarios.create_index("id_usuario", unique=True)
        self.perfiles_cvv.create_index("estudiante_id", unique=True)

    def verificar_conexion(self):
        return self.cliente.admin.command("ping")

    def listar_ofertas_empresa(self, empresa_id):
        cursor = self.ofertas.find(
            {"empresa_id": empresa_id, "estado": "habilitada"}
        ).sort("fecha_publicacion", DESCENDING)
        ofertas = [self._serializar(documento) for documento in cursor]
        for oferta in ofertas:
            oferta["total_postulantes"] = self.postulaciones.count_documents(
                {"oferta_id": oferta["id"]}
            )
        return ofertas

    def listar_ofertas_disponibles(self, empresa_id, estudiante_id):
        postuladas = self.postulaciones.distinct(
            "oferta_id", {"estudiante_id": estudiante_id}
        )
        filtro = {
            "empresa_id": empresa_id,
            "estado": "habilitada",
            "_id": {"$nin": [ObjectId(valor) for valor in postuladas if self._es_object_id(valor)]},
        }
        cursor = self.ofertas.find(filtro).sort("fecha_publicacion", DESCENDING)
        return [self._serializar(documento) for documento in cursor]

    def crear_oferta(self, documento):
        resultado = self.ofertas.insert_one(documento)
        return self.obtener_oferta(str(resultado.inserted_id))

    def obtener_oferta(self, oferta_id):
        if not self._es_object_id(oferta_id):
            return None
        documento = self.ofertas.find_one({"_id": ObjectId(oferta_id)})
        return self._serializar(documento) if documento else None

    def crear_postulacion(self, documento):
        try:
            resultado = self.postulaciones.insert_one(documento)
        except DuplicateKeyError as error:
            raise ValueError("El estudiante ya postuló a esta oferta.") from error
        documento["_id"] = resultado.inserted_id
        return self._serializar(documento)

    def obtener_usuario(self, usuario_id):
        documento = self.usuarios.find_one({"id_usuario": usuario_id})
        return self._serializar(documento) if documento else None

    def obtener_perfil_cvv(self, estudiante_id):
        documento = self.perfiles_cvv.find_one(
            {"estudiante_id": estudiante_id}
        )
        return self._serializar(documento) if documento else None

    def actualizar_curriculum_perfil(
        self, estudiante_id, archivo_id, nombre_archivo
    ):
        self.perfiles_cvv.update_one(
            {"estudiante_id": estudiante_id},
            {
                "$set": {
                    "archivo_adjunto_id": archivo_id,
                    "archivo_adjunto_nombre": nombre_archivo,
                }
            },
        )

    def guardar_curriculum(self, contenido, nombre, tipo_contenido):
        archivo_id = self.archivos.put(
            contenido,
            filename=nombre,
            content_type=tipo_contenido,
        )
        return str(archivo_id)

    def eliminar_curriculum(self, archivo_id):
        if self._es_object_id(archivo_id):
            try:
                self.archivos.delete(ObjectId(archivo_id))
            except NoFile:
                pass

    def obtener_curriculum(self, archivo_id):
        if not self._es_object_id(archivo_id):
            return None
        try:
            return self.archivos.get(ObjectId(archivo_id))
        except NoFile:
            return None

    def listar_postulaciones_oferta(self, oferta_id, empresa_id):
        oferta = self.obtener_oferta(oferta_id)
        if not oferta or oferta.get("empresa_id") != empresa_id:
            return None
        cursor = self.postulaciones.find({"oferta_id": oferta_id}).sort(
            "fecha", DESCENDING
        )
        return [self._serializar(documento) for documento in cursor]

    @staticmethod
    def _es_object_id(valor):
        return ObjectId.is_valid(str(valor))

    @staticmethod
    def _serializar(documento):
        if not documento:
            return documento
        copia = dict(documento)
        copia["id"] = str(copia.pop("_id"))
        for campo, valor in list(copia.items()):
            if hasattr(valor, "isoformat"):
                copia[campo] = valor.isoformat()
        return copia
