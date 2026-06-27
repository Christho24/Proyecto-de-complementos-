class ControladorUsuarios:
    def __init__(self, base_datos):
        self.base_datos = base_datos

    def obtener_empresa(self, empresa_id):
        usuario = self._obtener_usuario(empresa_id)
        if usuario.get("tipo") != "empresa":
            raise ValueError("El usuario indicado no corresponde a una empresa.")
        return usuario

    def obtener_estudiante(self, estudiante_id):
        usuario = self._obtener_usuario(estudiante_id)
        if usuario.get("tipo") != "estudiante":
            raise ValueError(
                "El usuario indicado no corresponde a un estudiante."
            )
        perfil = self.base_datos.obtener_perfil_cvv(estudiante_id)
        if not perfil:
            raise ValueError("El estudiante no posee un PerfilCVV cargado.")
        return usuario, perfil

    def obtener_perfil(self, estudiante_id):
        _usuario, perfil = self.obtener_estudiante(estudiante_id)
        return perfil

    def obtener_usuario(self, usuario_id):
        return self._obtener_usuario(usuario_id)

    def _obtener_usuario(self, usuario_id):
        usuario = self.base_datos.obtener_usuario(usuario_id)
        if not usuario:
            raise ValueError(
                "El perfil solicitado no está cargado en la base de datos."
            )
        return usuario
