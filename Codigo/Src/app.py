from flask import Flask, jsonify, render_template
from pymongo.errors import PyMongoError

from config import Config
from acceso_datos.controlador_base_datos import ControladorBaseDatos
from logica_negocio.controlador_ofertas import ControladorOfertas
from logica_negocio.controlador_postulacion import ControladorPostulacion
from logica_negocio.controlador_usuarios import ControladorUsuarios
from rutas.api import crear_api


def crear_aplicacion(configuracion=None, base_datos=None):
    app = Flask(
        __name__,
        template_folder="presentacion",
        static_folder="presentacion",
        static_url_path="/presentacion",
    )
    app.config.from_object(Config)
    if configuracion:
        app.config.update(configuracion)

    db = base_datos or ControladorBaseDatos(
        app.config["MONGO_URI"], app.config["MONGO_DB"]
    )
    controlador_ofertas = ControladorOfertas(db)
    controlador_usuarios = ControladorUsuarios(db)
    controlador_postulacion = ControladorPostulacion(
        db, controlador_usuarios
    )

    app.register_blueprint(
        crear_api(
            controlador_ofertas,
            controlador_postulacion,
            controlador_usuarios,
            app.config,
        )
    )

    @app.get("/")
    def inicio():
        return render_template("inicio.html")

    @app.get("/empresa")
    def vista_empresa():
        empresa = controlador_usuarios.obtener_empresa(
            app.config["EMPRESA_DEMO_ID"]
        )
        return render_template(
            "empresa/ofertas.html",
            empresa_id=app.config["EMPRESA_DEMO_ID"],
            empresa=empresa,
            empresa_iniciales=_iniciales(empresa["nombre_empresa"]),
        )

    @app.get("/estudiante")
    def vista_estudiante():
        empresa = controlador_usuarios.obtener_empresa(
            app.config["EMPRESA_DEMO_ID"]
        )
        estudiante, perfil = controlador_usuarios.obtener_estudiante(
            app.config["ESTUDIANTE_DEMO_ID"]
        )
        return render_template(
            "estudiante/ofertas.html",
            empresa_id=app.config["EMPRESA_DEMO_ID"],
            estudiante_id=app.config["ESTUDIANTE_DEMO_ID"],
            empresa=empresa,
            estudiante=estudiante,
            perfil=perfil,
            empresa_iniciales=_iniciales(empresa["nombre_empresa"]),
            estudiante_iniciales=_iniciales(estudiante["nombre"]),
        )

    @app.get("/api/salud")
    def salud():
        db.verificar_conexion()
        return jsonify({"estado": "ok", "base_datos": app.config["MONGO_DB"]})

    @app.errorhandler(ValueError)
    def manejar_validacion(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(PyMongoError)
    def manejar_mongo(error):
        app.logger.exception("Error de MongoDB")
        return jsonify(
            {
                "error": (
                    "No fue posible acceder a MongoDB. "
                    "Verifique que esté disponible en el puerto 18000."
                )
            }
        ), 503

    @app.errorhandler(404)
    def no_encontrado(_error):
        return jsonify({"error": "Recurso no encontrado."}), 404

    @app.errorhandler(413)
    def archivo_demasiado_grande(_error):
        return jsonify({"error": "El archivo supera el máximo permitido de 5 MB."}), 413

    return app


def _iniciales(nombre):
    return "".join(
        parte[0] for parte in nombre.split()[:2] if parte
    ).upper()


app = crear_aplicacion()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
