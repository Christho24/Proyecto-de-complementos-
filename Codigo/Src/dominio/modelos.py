from dataclasses import asdict, dataclass
from datetime import datetime, timezone


MODALIDADES = {"Presencial", "Remota", "Híbrida"}
JORNADAS = {"Tiempo completo", "Tiempo parcial"}


def ahora_utc():
    return datetime.now(timezone.utc)


@dataclass
class Oferta:
    empresa_id: str
    titulo: str
    descripcion: str
    carrera: str
    sueldo_min: int
    sueldo_max: int
    jornada: str
    ubicacion: str
    modalidad: str
    estado: str = "habilitada"

    def validar(self):
        campos = {
            "empresa_id": self.empresa_id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "carrera": self.carrera,
            "jornada": self.jornada,
            "ubicacion": self.ubicacion,
            "modalidad": self.modalidad,
        }
        vacios = [nombre for nombre, valor in campos.items() if not str(valor).strip()]
        if vacios:
            raise ValueError(f"Faltan campos obligatorios: {', '.join(vacios)}.")
        if self.sueldo_min < 0 or self.sueldo_max < self.sueldo_min:
            raise ValueError("El rango de sueldo no es válido.")
        if self.modalidad not in MODALIDADES:
            raise ValueError("La modalidad seleccionada no es válida.")
        if self.jornada not in JORNADAS:
            raise ValueError("La jornada seleccionada no es válida.")

    def a_documento(self):
        self.validar()
        documento = asdict(self)
        documento["fecha_publicacion"] = ahora_utc()
        return documento


@dataclass
class Postulacion:
    oferta_id: str
    estudiante_id: str
    estudiante_nombre: str
    cv_archivo_id: str
    cv_nombre: str
    carta_presentacion: str = ""
    estado: str = "enviada"

    def validar(self):
        if not all(
            (
                self.oferta_id,
                self.estudiante_id,
                self.estudiante_nombre,
                self.cv_archivo_id,
                self.cv_nombre,
            )
        ):
            raise ValueError(
                "La oferta, el estudiante y el currículum son obligatorios."
            )
        if len(self.carta_presentacion) > 1500:
            raise ValueError("La carta de presentación no puede superar 1500 caracteres.")

    def a_documento(self):
        self.validar()
        documento = asdict(self)
        documento["fecha"] = ahora_utc()
        return documento
