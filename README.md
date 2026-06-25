# Finis Trabaja — entrega funcional

Prototipo web de los dos flujos solicitados:

1. Una empresa visualiza sus ofertas habilitadas y puede publicar una nueva.
2. Un estudiante visualiza las ofertas de esa empresa y postula a una. La oferta
   postulada deja de aparecer para ese estudiante, incluso después de actualizar.

No incluye registro, inicio de sesión, administración ni recomendaciones. La
empresa, el estudiante y su PerfilCVV son datos de demostración precargados.

## Arquitectura

El código está en `Codigo/Src/` y sigue la planificación del proyecto:

```text
presentacion/       HTML + CSS + JavaScript
       ↓ API REST
logica_negocio/     Controladores de ofertas, postulaciones y usuarios
       ↓
acceso_datos/       ControladorBaseDatos
       ↓
MongoDB             Usuarios, PerfilCVV, Ofertas y Postulaciones
```

Las entidades implementadas conservan los atributos del diagrama de clases:
`Ofertas` (título, descripción, carrera, rango de sueldo, jornada, ubicación y
modalidad), `Postulacion` (fecha y estado), `Usuarios` y `PerfilCVV`.

## Ejecución recomendada con Docker

Requisito: Docker Desktop.

```powershell
cd Codigo\Src
docker compose up -d --build
docker compose exec web python scripts/cargar_datos_demo.py
```

Abrir <http://localhost:5000>. MongoDB queda expuesto en
`mongodb://localhost:18000/`, tal como exige la entrega.

Para detener:

```powershell
docker compose down
```

Para borrar también los datos persistidos:

```powershell
docker compose down -v
```

## Ejecución local

Con MongoDB ejecutándose en el puerto `18000`:

```powershell
cd Codigo\Src
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\cargar_datos_demo.py
python app.py
```

## Direcciones de demostración

- Inicio: <http://localhost:5000/>
- Empresa: <http://localhost:5000/empresa>
- Estudiante: <http://localhost:5000/estudiante>
- Salud de API: <http://localhost:5000/api/salud>

Los IDs de empresa y estudiante solo seleccionan los perfiles precargados desde
MongoDB; no implementan autenticación.

## Pruebas

Desde `Codigo/Src/`:

```powershell
python -m unittest discover -s tests -v
```

Las pruebas verifican creación y listado de ofertas, carga de perfiles desde la
capa de datos, postulación con CV, revisión de postulantes, desaparición de una
oferta postulada, bloqueo de duplicados y validaciones principales.

## Integrantes

- Christopher Abarca
- Benjamín Echeverría
- Maico Huillca
- Camila Romero
