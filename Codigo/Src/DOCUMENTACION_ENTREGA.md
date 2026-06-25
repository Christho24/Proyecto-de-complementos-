# Correspondencia con la planificación y pauta

## Alcance implementado

| Funcionalidad solicitada | Implementación |
|---|---|
| Empresa visualiza ofertas habilitadas | `GET /api/empresas/{id}/ofertas` y vista `/empresa` |
| Nueva oferta persiste después de actualizar | Formulario de empresa, `POST /api/empresas/{id}/ofertas` y colección `Ofertas` |
| Estudiante visualiza ofertas de una empresa | `GET /api/empresas/{id}/ofertas/disponibles` y vista `/estudiante` |
| Estudiante postula a una oferta | `POST /api/ofertas/{id}/postulaciones` |
| Estudiante adjunta su CV | PDF almacenado por la capa de datos al postular |
| Empresa revisa postulantes | Listado por oferta con nombre, fecha, carta y descarga de CV |
| Oferta postulada deja de mostrarse | Exclusión en MongoDB usando las postulaciones del estudiante |
| Datos de demostración | `scripts/cargar_datos_demo.py` |
| MongoDB en puerto 18000 | `docker-compose.yml`, mapeo `18000:27017` |
| Perfiles demo desde MongoDB | Colecciones `Usuarios` y `PerfilCVV`, sin login ni registro |

## Correspondencia con el diagrama de clases

La clase `Oferta` implementa:

- `idOferta`: generado por MongoDB como `_id`.
- `titulo`.
- `descripcion`.
- `carrera`.
- `sueldoMin` y `sueldoMax`: representados como `sueldo_min` y `sueldo_max`.
- `jornada`.
- `ubicacion`.
- `modalidad`.
- operación `publicar`: implementada por `ControladorOfertas.publicar`.

La clase `Postulacion` implementa:

- `idPostulacion`: generado por MongoDB como `_id`.
- `fecha`.
- `estado`.
- operación `registrarPostulacion`: implementada por
  `ControladorPostulacion.registrar`.
- El archivo adjunto del `PerfilCCV` se representa mediante el CV PDF asociado
  a la postulación, de modo que la empresa pueda revisarlo según RU15.

Se agregan `empresa_id` y `estudiante_id` exclusivamente para materializar las
asociaciones dibujadas entre empresa, oferta, estudiante y postulación.

## Correspondencia con la arquitectura

- **Capa de presentación:** `presentacion/`, con un HTML, CSS y JavaScript
  separados por interfaz.
- **Capa de lógica de negocio:** `logica_negocio/`, con los controladores de
  ofertas y postulaciones indicados en la planificación.
- **Capa de acceso a datos:** `acceso_datos/controlador_base_datos.py`, único
  punto de comunicación con MongoDB.
- **Capa de datos:** colecciones `Usuarios`, `PerfilCVV`, `Ofertas` y
  `Postulaciones`.

## Decisiones de alcance

- No existe autenticación ni registro.
- La empresa y el estudiante son perfiles precargados en MongoDB. Los IDs de
  configuración solo seleccionan qué perfil demo mostrar.
- No se implementa la edición completa del Perfil CVV, administración ni
  recomendación. El CV requerido se actualiza en `PerfilCVV` al postular.
- La carta de presentación es opcional, de acuerdo con RU14/RS54.
- La combinación oferta-estudiante tiene un índice único para impedir una
  postulación duplicada.

## Guion breve para la evaluación

1. Abrir `/empresa` y mostrar las ofertas cargadas desde MongoDB.
2. Publicar una oferta y actualizar el navegador; la oferta permanece.
3. Abrir `/estudiante`; la oferta nueva aparece en el listado.
4. Postular a esa oferta; desaparece inmediatamente.
5. Actualizar `/estudiante`; la oferta sigue sin aparecer porque la
   postulación está persistida en MongoDB.
6. Volver a `/empresa`; la oferta continúa habilitada y visible para la
   empresa, pues postular no elimina la vacante.
