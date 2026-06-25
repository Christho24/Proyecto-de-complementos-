from dominio.modelos import Postulacion


class ControladorPostulacion:
    def __init__(self, base_datos, controlador_usuarios):
        self.base_datos = base_datos
        self.controlador_usuarios = controlador_usuarios

    def registrar(
        self,
        oferta_id,
        estudiante_id,
        curriculum,
        carta_presentacion="",
    ):
        oferta = self.base_datos.obtener_oferta(oferta_id)
        if not oferta or oferta.get("estado") != "habilitada":
            raise ValueError("La oferta no existe o ya no está habilitada.")

        estudiante, _perfil = self.controlador_usuarios.obtener_estudiante(
            estudiante_id
        )
        self._validar_curriculum(curriculum)
        contenido = curriculum.read()
        if len(contenido) > 5 * 1024 * 1024:
            raise ValueError("El currículum no puede superar 5 MB.")

        archivo_id = self.base_datos.guardar_curriculum(
            contenido,
            curriculum.filename,
            curriculum.mimetype or "application/pdf",
        )
        postulacion = Postulacion(
            oferta_id=oferta_id,
            estudiante_id=estudiante_id,
            estudiante_nombre=estudiante["nombre"],
            cv_archivo_id=archivo_id,
            cv_nombre=curriculum.filename,
            carta_presentacion=str(carta_presentacion or "").strip(),
        )
        try:
            resultado = self.base_datos.crear_postulacion(
                postulacion.a_documento()
            )
            self.base_datos.actualizar_curriculum_perfil(
                estudiante_id, archivo_id, curriculum.filename
            )
            return resultado
        except Exception:
            self.base_datos.eliminar_curriculum(archivo_id)
            raise

    def listar_por_oferta(self, oferta_id, empresa_id):
        postulaciones = self.base_datos.listar_postulaciones_oferta(
            oferta_id, empresa_id
        )
        if postulaciones is None:
            raise ValueError("La oferta no pertenece a la empresa indicada.")
        return postulaciones

    def obtener_curriculum(self, archivo_id):
        archivo = self.base_datos.obtener_curriculum(archivo_id)
        if not archivo:
            raise ValueError("El currículum solicitado no existe.")
        return archivo

    @staticmethod
    def _validar_curriculum(curriculum):
        if not curriculum or not curriculum.filename:
            raise ValueError("Debe adjuntar el currículum en formato PDF.")
        if not curriculum.filename.lower().endswith(".pdf"):
            raise ValueError("El currículum debe ser un archivo PDF.")
