from django.db import models

# Create your models here.
# Tablas de la base de datos
class Usuario(models.Model):

    #Parametros de la tabla
    correo = models.EmailField(primary_key=True)
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

    #id automatico sera la llave
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    semestre = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    seccion = models.PositiveIntegerField()

    class Meta:
        db_table = "Cursos"

    def __str__(self):
        #definir como ver las filas de la tabla
        return self.nombre + " " + self.codigo + " " + self.semestre + " " + self.año + " " + self.seccion

class Alumnos(models.Model):

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    presento = models.BooleanField()
    rut = models.PositiveIntegerField(primary_key=True)
    codigoVerificador = models.CharField(max_length=1)

    class Meta:
        db_table = "Alumnos"

    def __str__(self):
        return self.rut + " " + self.codigoVerificador

class Rubrica(models.Model):
    
    #id es automatico
    nombre = models.CharField(max_length=50,primary_key=True)
    version = models.CharField(max_length=50)
    tiempo = models.DurationField()
    archivo = models.FilePathField()

    class Meta:
        db_table = "Rubrica"

    def __str__(self):
        return self.nombre + " " + self.version

class Evaluacion(models.Model):
    
    #id es automatico
    fecha = models.DateTimeField()
    estado = models.CharField(max_length=50)
    duracion = models.DurationField()

    class Meta:
        db_table = "Evaluacion"

    def __str__(self):
        return "Evaluacion: " + self.fecha
        

##############################################################
#Tablas conectoras

class Usuario_Evaluacion(models.Model):

    def __str__(self):
        #return self.correo + " " + self.idEvaluacion
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