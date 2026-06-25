from io import BytesIO

from flask import Blueprint, jsonify, request, send_file


def crear_api(
    controlador_ofertas,
    controlador_postulacion,
    controlador_usuarios,
    config,
):
    api = Blueprint("api", __name__, url_prefix="/api")

    @api.get("/empresas/<empresa_id>/ofertas")
    def ofertas_empresa(empresa_id):
        ofertas = controlador_ofertas.listar_habilitadas(empresa_id)
        return jsonify({"datos": ofertas, "total": len(ofertas)})

    @api.post("/empresas/<empresa_id>/ofertas")
    def publicar_oferta(empresa_id):
        oferta = controlador_ofertas.publicar(
            empresa_id, request.get_json(silent=True) or {}
        )
        return jsonify({"mensaje": "Oferta publicada correctamente.", "datos": oferta}), 201

    @api.get("/empresas/<empresa_id>/ofertas/disponibles")
    def ofertas_disponibles(empresa_id):
        estudiante_id = request.args.get(
            "estudiante_id", config["ESTUDIANTE_DEMO_ID"]
        )
        ofertas = controlador_ofertas.listar_disponibles(
            empresa_id, estudiante_id
        )
        return jsonify({"datos": ofertas, "total": len(ofertas)})

    @api.post("/ofertas/<oferta_id>/postulaciones")
    def postular(oferta_id):
        postulacion = controlador_postulacion.registrar(
            oferta_id=oferta_id,
            estudiante_id=request.form.get(
                "estudiante_id", config["ESTUDIANTE_DEMO_ID"]
            ),
            curriculum=request.files.get("curriculum"),
            carta_presentacion=request.form.get("carta_presentacion", ""),
        )

    @api.get("/usuarios/<usuario_id>")
    def obtener_usuario(usuario_id):
        usuario = controlador_usuarios.obtener_usuario(usuario_id)
        return jsonify({"datos": usuario})

    @api.get("/estudiantes/<estudiante_id>/perfil-cvv")
    def obtener_perfil_cvv(estudiante_id):
        perfil = controlador_usuarios.obtener_perfil(estudiante_id)
        return jsonify({"datos": perfil})
        return jsonify(
            {
                "mensaje": "Postulación enviada correctamente.",
                "datos": postulacion,
            }
        ), 201

    @api.get("/ofertas/<oferta_id>/postulaciones")
    def postulaciones_oferta(oferta_id):
        empresa_id = request.args.get("empresa_id", config["EMPRESA_DEMO_ID"])
        postulaciones = controlador_postulacion.listar_por_oferta(
            oferta_id, empresa_id
        )
        return jsonify(
            {"datos": postulaciones, "total": len(postulaciones)}
        )

    @api.get("/curriculums/<archivo_id>")
    def descargar_curriculum(archivo_id):
        archivo = controlador_postulacion.obtener_curriculum(archivo_id)
        return send_file(
            BytesIO(archivo.read()),
            mimetype=getattr(archivo, "content_type", "application/pdf"),
            as_attachment=True,
            download_name=archivo.filename or "curriculum.pdf",
        )

    return api
