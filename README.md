# Finis Trabaja

Prototipo web para gestionar ofertas laborales y postulaciones de estudiantes.

La aplicacion permite:

1. Que una empresa publique, visualice y elimine ofertas habilitadas.
2. Que un estudiante visualice todas las ofertas de la empresa y postule a una.
3. Que la empresa revise postulantes, cartas de presentacion y CV enviados.
4. Que el estudiante postule usando un PDF propio o su PerfilCVV de la plataforma.

El codigo de la aplicacion esta en `Codigo/Src/`.

## Ejecucion Recomendada Con Docker

Requisito: tener Docker Desktop abierto.

Desde la raiz del proyecto:

```powershell
cd Codigo\Src
docker compose up -d --build
docker compose exec web python scripts/cargar_datos_demo.py
```

Luego abrir:

- Inicio: http://localhost:5000/
- Vista empresa: http://localhost:5000/empresa
- Vista estudiante: http://localhost:5000/estudiante
- Salud de API: http://localhost:5000/api/salud

MongoDB queda disponible en:

```text
mongodb://localhost:18000/
```

## Detener Los Servicios

Desde `Codigo/Src/`:

```powershell
docker compose down
```

Para detener y borrar tambien los datos guardados en MongoDB:

```powershell
docker compose down -v
```

## Ejecucion Local Sin Docker

Requisito: tener MongoDB ejecutandose en el puerto `18000`.

Desde la raiz del proyecto:

```powershell
cd Codigo\Src
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\cargar_datos_demo.py
python app.py
```

Luego abrir http://localhost:5000/.

## Ejecutar Pruebas

Con Docker:

```powershell
cd Codigo\Src
docker compose exec web python -m unittest discover -s tests -v
```

Sin Docker, desde `Codigo/Src/` y con las dependencias instaladas:

```powershell
python -m unittest discover -s tests -v
```

## Arquitectura

```text
presentacion/       HTML + CSS + JavaScript
       -> API REST
logica_negocio/     Controladores de ofertas, postulaciones y usuarios
       ->
acceso_datos/       ControladorBaseDatos
       ->
MongoDB             Usuarios, PerfilCVV, Ofertas, Postulaciones y Curriculums
```

## Integrantes

- Christopher Abarca
- Benjamin Echeverria
- Maico Huillca
- Camila Romero
