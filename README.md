# Nexo Digital

Proyecto Django de tienda de equipos y soluciones de telecomunicaciones.

## Requisitos

- Python 3.12+
- Virtual environment (`venv`)
- Dependencias en `requirements.txt`

## Instalación

1. Abre la terminal en la raíz del proyecto:

```bash
cd /home/renato/Nexo-Digital
```

2. Crea y activa el entorno virtual (si aún no existe):

```bash
python3 -m venv env
source env/bin/activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecuta las migraciones:

```bash
python manage.py migrate
```

5. Inicia el servidor de desarrollo:

```bash
python manage.py runserver
```

6. Abre la aplicación en el navegador:

```text
http://localhost:8000/
```

## Notas

- Si necesitas ejecutar desde otra carpeta, ajusta la ruta al proyecto.
- Si agregas nuevos archivos estáticos, Django los sirve automáticamente en modo de desarrollo.
- Para producción, recuerda usar `python manage.py collectstatic` y un servidor web adecuado.
