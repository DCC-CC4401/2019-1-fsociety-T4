# 2019-1-fsociety-T4

## Activar enviroment de python3

    source pyenv/bin/activate

## Para que el proyecto reconozca la base de datos hacer lo siguiente

    python manage.py makemigrations EvPresentaciones
    python manage.py migrate EvPresentaciones
    python manage.py migrate
    
## Existe un dump con datos minimos para mostrar en consultas, se llama db.json

## Crear dump

    python manage.py dumpdata > db.json
    
## Cargar dump

    python manage.py loaddata db.json

## Crear superusuario

    python3 manage.py createsuperuser 