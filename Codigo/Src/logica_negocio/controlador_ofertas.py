from dominio.modelos import Oferta


class ControladorOfertas:
    def __init__(self, base_datos):
        self.base_datos = base_datos

    def listar_habilitadas(self, empresa_id):
        if not empresa_id:
            raise ValueError("Debe indicar una empresa.")
        return self.base_datos.listar_ofertas_empresa(empresa_id)

    def listar_disponibles(self, empresa_id, estudiante_id):
        if not empresa_id or not estudiante_id:
            raise ValueError("Debe indicar empresa y estudiante.")
        return self.base_datos.listar_ofertas_disponibles(
            empresa_id, estudiante_id
        )

    def listar_para_estudiante(self, empresa_id, estudiante_id):
        if not empresa_id or not estudiante_id:
            raise ValueError("Debe indicar empresa y estudiante.")
        return self.base_datos.listar_ofertas_estudiante(
            empresa_id, estudiante_id
        )

    def publicar(self, empresa_id, datos):
        oferta = Oferta(
            empresa_id=empresa_id,
            titulo=str(datos.get("titulo", "")).strip(),
            descripcion=str(datos.get("descripcion", "")).strip(),
            carrera=str(datos.get("carrera", "")).strip(),
            sueldo_min=self._entero(datos.get("sueldo_min"), "sueldo mínimo"),
            sueldo_max=self._entero(datos.get("sueldo_max"), "sueldo máximo"),
            jornada=str(datos.get("jornada", "")).strip(),
            ubicacion=str(datos.get("ubicacion", "")).strip(),
            modalidad=str(datos.get("modalidad", "")).strip(),
        )
        return self.base_datos.crear_oferta(oferta.a_documento())

    def eliminar(self, empresa_id, oferta_id):
        if not empresa_id or not oferta_id:
            raise ValueError("Debe indicar empresa y oferta.")
        eliminada = self.base_datos.eliminar_oferta(oferta_id, empresa_id)
        if not eliminada:
            raise ValueError("La oferta no existe o no pertenece a la empresa.")
        return {"id": oferta_id, "estado": "eliminada"}

    @staticmethod
    def _entero(valor, nombre):
        try:
            return int(valor)
        except (TypeError, ValueError) as error:
            raise ValueError(f"El {nombre} debe ser un número entero.") from error
