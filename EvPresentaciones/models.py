from django.db import models

# Create your models here.
# Tablas de la base de datos
class Usuario(models.Model):

    #Parametros de la tabla
    correo = models.CharField(max_length=100,primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    esAdministrador = models.BooleanField()
    contrasena = models.CharField(max_length=50)

    #Para linkear las tablas
    class Meta:
        db_table = "Usuario"

    def __str__(self):
        #definir como ver las filas de la tabla
        return self.correo

class Cursos(models.Model):

    #Definir los parametros de las tablas

    def __str__(self):
        #definir como ver las filas de la tabla
        pass

class Alumnos(models.Model):

    #Definir los parametros de las tablas

    def __str__(self):
        #definir como ver las filas de la tabla
        pass

class Rubrica(models.Model):
    
    

    def __str__(self):
        #definir como ver las filas de la tabla
        pass


##############################################################
#Tablas conectoras

class Usuario_Evaluacion(models.Model):
    
    #Definir los parametros de las tablas

    def __str__(self):
        #definir como ver las filas de la tabla
        pass

class Evaluacion_Rubrica(models.Model):
    
    #Definir los parametros de las tablas

    def __str__(self):
        #definir como ver las filas de la tabla
        pass

class Cursos_Evaluacion(models.Model):
    
    #Definir los parametros de las tablas

    def __str__(self):
        #definir como ver las filas de la tabla
        pass

class Cursos_Alumnos(models.Model):
    
    #Definir los parametros de las tablas

    def __str__(self):
        #definir como ver las filas de la tabla
        pass

class Alumnos_Evaluacion(models.Model):
    
    #Definir los parametros de las tablas

    def __str__(self):
        #definir como ver las filas de la tabla
        pass