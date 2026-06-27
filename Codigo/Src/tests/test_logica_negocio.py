import unittest
from io import BytesIO

from dominio.modelos import Oferta
from logica_negocio.controlador_ofertas import ControladorOfertas
from logica_negocio.controlador_postulacion import ControladorPostulacion
from logica_negocio.controlador_usuarios import ControladorUsuarios


class BaseDatosFalsa:
    def __init__(self):
        self.ofertas = []
        self.postulaciones = []
        self.archivos = {}
        self.usuarios = {
            "empresa_1": {
                "id": "empresa_1",
                "id_usuario": "empresa_1",
                "tipo": "empresa",
                "nombre_empresa": "Empresa de prueba",
            },
            "estudiante_1": {
                "id": "estudiante_1",
                "id_usuario": "estudiante_1",
                "tipo": "estudiante",
                "nombre": "Estudiante de prueba",
            },
        }
        self.perfil = {
            "id": "perfil_1",
            "estudiante_id": "estudiante_1",
            "carrera": "Ingeniería Civil Informática",
        }

    def crear_oferta(self, documento):
        documento = {**documento, "id": str(len(self.ofertas) + 1)}
        self.ofertas.append(documento)
        return documento

    def eliminar_oferta(self, oferta_id, empresa_id):
        oferta = self.obtener_oferta(oferta_id)
        if (
            not oferta
            or oferta["empresa_id"] != empresa_id
            or oferta["estado"] != "habilitada"
        ):
            return False
        oferta["estado"] = "eliminada"
        return True

    def listar_ofertas_empresa(self, empresa_id):
        return [
            oferta for oferta in self.ofertas
            if oferta["empresa_id"] == empresa_id and oferta["estado"] == "habilitada"
        ]

    def listar_ofertas_disponibles(self, empresa_id, estudiante_id):
        ids_postulados = {
            postulacion["oferta_id"]
            for postulacion in self.postulaciones
            if postulacion["estudiante_id"] == estudiante_id
        }
        return [
            oferta for oferta in self.listar_ofertas_empresa(empresa_id)
            if oferta["id"] not in ids_postulados
        ]

    def listar_ofertas_estudiante(self, empresa_id, estudiante_id):
        ids_postulados = {
            postulacion["oferta_id"]
            for postulacion in self.postulaciones
            if postulacion["estudiante_id"] == estudiante_id
        }
        return [
            {**oferta, "postulada": oferta["id"] in ids_postulados}
            for oferta in self.listar_ofertas_empresa(empresa_id)
        ]

    def obtener_oferta(self, oferta_id):
        return next(
            (oferta for oferta in self.ofertas if oferta["id"] == oferta_id),
            None,
        )

    def crear_postulacion(self, documento):
        duplicada = any(
            item["oferta_id"] == documento["oferta_id"]
            and item["estudiante_id"] == documento["estudiante_id"]
            for item in self.postulaciones
        )
        if duplicada:
            raise ValueError("El estudiante ya postuló a esta oferta.")
        documento = {**documento, "id": str(len(self.postulaciones) + 1)}
        self.postulaciones.append(documento)
        return documento

    def guardar_curriculum(self, contenido, nombre, tipo_contenido):
        archivo_id = str(len(self.archivos) + 1)
        self.archivos[archivo_id] = {
            "contenido": contenido,
            "nombre": nombre,
            "tipo": tipo_contenido,
        }
        return archivo_id

    def eliminar_curriculum(self, archivo_id):
        self.archivos.pop(archivo_id, None)

    def obtener_usuario(self, usuario_id):
        return self.usuarios.get(usuario_id)

    def obtener_perfil_cvv(self, estudiante_id):
        return self.perfil if estudiante_id == "estudiante_1" else None

    def actualizar_curriculum_perfil(
        self, estudiante_id, archivo_id, nombre_archivo
    ):
        self.perfil["archivo_adjunto_id"] = archivo_id
        self.perfil["archivo_adjunto_nombre"] = nombre_archivo

    def listar_postulaciones_oferta(self, oferta_id, empresa_id):
        oferta = self.obtener_oferta(oferta_id)
        if not oferta or oferta["empresa_id"] != empresa_id:
            return None
        return [
            item for item in self.postulaciones
            if item["oferta_id"] == oferta_id
        ]


class CurriculumFalso(BytesIO):
    filename = "cv_camila_rojas.pdf"
    mimetype = "application/pdf"

    def __init__(self):
        super().__init__(b"%PDF-1.4 curriculum demo")


class FlujosEntregaTest(unittest.TestCase):
    def setUp(self):
        self.db = BaseDatosFalsa()
        self.ofertas = ControladorOfertas(self.db)
        self.usuarios = ControladorUsuarios(self.db)
        self.postulaciones = ControladorPostulacion(self.db, self.usuarios)
        self.datos = {
            "titulo": "Desarrollador Backend Junior",
            "descripcion": "Desarrollo de APIs y pruebas.",
            "carrera": "Ingeniería Civil Informática",
            "sueldo_min": 800000,
            "sueldo_max": 1100000,
            "jornada": "Tiempo completo",
            "ubicacion": "Santiago, Chile",
            "modalidad": "Híbrida",
        }

    def postular(self, oferta_id, estudiante_id="estudiante_1"):
        return self.postulaciones.registrar(
            oferta_id,
            estudiante_id,
            CurriculumFalso(),
            carta_presentacion="Me interesa esta oportunidad.",
        )

    def test_oferta_publicada_aparece_en_listado_empresa(self):
        creada = self.ofertas.publicar("empresa_1", self.datos)
        listado = self.ofertas.listar_habilitadas("empresa_1")
        self.assertEqual(listado[0]["id"], creada["id"])

    def test_empresa_puede_eliminar_oferta(self):
        creada = self.ofertas.publicar("empresa_1", self.datos)
        resultado = self.ofertas.eliminar("empresa_1", creada["id"])
        self.assertEqual(resultado["estado"], "eliminada")
        self.assertEqual(self.ofertas.listar_habilitadas("empresa_1"), [])
        self.assertEqual(
            self.ofertas.listar_para_estudiante("empresa_1", "estudiante_1"),
            [],
        )

    def test_oferta_postulada_sigue_visible_y_marcada_para_estudiante(self):
        creada = self.ofertas.publicar("empresa_1", self.datos)
        self.postular(creada["id"])
        ofertas = self.ofertas.listar_para_estudiante("empresa_1", "estudiante_1")
        self.assertEqual(ofertas[0]["id"], creada["id"])
        self.assertTrue(ofertas[0]["postulada"])

    def test_no_permite_postular_dos_veces(self):
        creada = self.ofertas.publicar("empresa_1", self.datos)
        self.postular(creada["id"])
        with self.assertRaisesRegex(ValueError, "ya postuló"):
            self.postular(creada["id"])

    def test_valida_rango_de_sueldo(self):
        datos = {**self.datos, "sueldo_min": 1000000, "sueldo_max": 500000}
        with self.assertRaisesRegex(ValueError, "rango de sueldo"):
            self.ofertas.publicar("empresa_1", datos)

    def test_modelo_respeta_atributos_del_diagrama(self):
        oferta = Oferta(empresa_id="empresa_1", **self.datos)
        documento = oferta.a_documento()
        for atributo in (
            "titulo", "descripcion", "carrera", "sueldo_min", "sueldo_max",
            "jornada", "ubicacion", "modalidad",
        ):
            self.assertIn(atributo, documento)

    def test_empresa_visualiza_postulante_y_curriculum(self):
        creada = self.ofertas.publicar("empresa_1", self.datos)
        postulacion = self.postular(creada["id"])
        listado = self.postulaciones.listar_por_oferta(
            creada["id"], "empresa_1"
        )
        self.assertEqual(
            listado[0]["estudiante_nombre"], "Estudiante de prueba"
        )
        self.assertEqual(listado[0]["cv_archivo_id"], postulacion["cv_archivo_id"])
        self.assertNotIn("archivo_adjunto_id", self.db.perfil)

    def test_postulacion_puede_usar_perfil_cvv_sin_crear_archivo(self):
        creada = self.ofertas.publicar("empresa_1", self.datos)
        postulacion = self.postulaciones.registrar(
            creada["id"],
            "estudiante_1",
            None,
            origen_cv="plataforma",
            carta_presentacion="Uso mi PerfilCVV.",
        )
        self.assertEqual(postulacion["origen_cv"], "plataforma")
        self.assertEqual(postulacion["cv_archivo_id"], "")
        self.assertEqual(postulacion["perfil_cvv"]["carrera"], self.db.perfil["carrera"])
        self.assertEqual(self.db.archivos, {})

    def test_curriculum_debe_ser_pdf(self):
        creada = self.ofertas.publicar("empresa_1", self.datos)
        archivo = CurriculumFalso()
        archivo.filename = "cv.docx"
        with self.assertRaisesRegex(ValueError, "PDF"):
            self.postulaciones.registrar(
                creada["id"],
                "estudiante_1",
                archivo,
            )

    def test_perfiles_se_obtienen_desde_capa_de_datos(self):
        empresa = self.usuarios.obtener_empresa("empresa_1")
        estudiante, perfil = self.usuarios.obtener_estudiante("estudiante_1")
        self.assertEqual(empresa["nombre_empresa"], "Empresa de prueba")
        self.assertEqual(estudiante["nombre"], "Estudiante de prueba")
        self.assertEqual(perfil["estudiante_id"], "estudiante_1")


if __name__ == "__main__":
    unittest.main()
