# 2019-1-fsociety-T4

## IMPORTANTE

    Ahora los usuarios de EvPresentaciones y del sitio Admin están unificados.
    Por favor:
     
      1. Volver a hacer las migraciones
      2. Crear un superusuario.
      3. Mirar  models.UsuarioManager y models.Usuario
      
    Las credenciales del superusuario deben servir para ingresar a la aplicación.
      
    Preguntas a Ariel
         
    

## Activar enviroment de python3

    source venv/bin/activate

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
