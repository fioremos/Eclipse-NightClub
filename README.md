# Eclipse Night Club

Proyecto Django para el sitio web de Eclipse Night Club, con formularios de contacto, vistas públicas, administración y una API interna para consultar registros almacenados en PostgreSQL.

## 1. Clonar y preparar el entorno

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar PostgreSQL

Crear una base de datos local en PostgreSQL:

```sql
CREATE DATABASE eclipse;
CREATE USER eclipse_user WITH PASSWORD 'tu_password';
ALTER ROLE eclipse_user SET client_encoding TO 'utf8';
ALTER ROLE eclipse_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE eclipse_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE eclipse TO eclipse_user;
```

Luego, en el archivo [mi_sitio/settings.py](mi_sitio/settings.py), ajustar los valores de conexión de la base de datos:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eclipse',
        'USER': 'eclipse_user',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Los campos que normalmente hay que modificar son:
- NAME: nombre de la base de datos
- USER: usuario de PostgreSQL
- PASSWORD: contraseña del usuario
- HOST: generalmente localhost
- PORT: normalmente 5432

## 3. Ejecutar migraciones

```bash
python manage.py migrate
```

## 4. Crear un superusuario

```bash
python manage.py createsuperuser
```

## 5. Levantar el proyecto

```bash
python manage.py runserver
```

Abrir en el navegador:
- Sitio: http://127.0.0.1:8000/


## APIs del proyecto
- API interna (JSON): /api/consultas/
- API externa consumida: https://api.tvmaze.com/search/shows?q=festival

## Nota
Para un entorno de producción, conviene mover secretos como la contraseña de la base de datos y la clave secreta a variables de entorno en vez de dejarlos hardcodeados en el proyecto.
