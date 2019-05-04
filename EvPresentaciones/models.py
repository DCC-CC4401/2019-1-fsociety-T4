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

    def isAdmin(self):
        #retorna si es admin o no
        return self.esAdministrador

class Cursos(models.Model):

    #id automatico sera la llave
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    semestre = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    seccion = models.PositiveIntegerField()

    class Meta:
        db_table = "Cursos"
        unique_together = (("codigo","semestre","año","seccion"),)

    def __str__(self):
        #definir como ver las filas de la tabla
        return self.nombre + " " + self.codigo + " " + self.semestre + " " + str(self.año) + " " + str(self.seccion)

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
    archivo = models.FilePathField(path="./", default="./")

    class Meta:
        db_table = "Rubrica"

    def __str__(self):
        return self.nombre + " " + self.version

class Evaluacion(models.Model):
    
    #id es automatico
    fechaInicio = models.DateTimeField()
    fechaTermino = models.DateTimeField()
    estado = models.CharField(max_length=50)
    duracion = models.DurationField()

    class Meta:
        db_table = "Evaluacion"

    def __str__(self):
        return "Evaluacion: " + str(self.id)
        

##############################################################
#Tablas conectoras

class Usuario_Evaluacion(models.Model):

    user = models.ForeignKey(Usuario,on_delete = models.CASCADE, null=True)
    evaluacion = models.ForeignKey(Evaluacion, on_delete = models.CASCADE, null=True)

    class Meta:
        unique_together = (("user", "evaluacion"),)

    def __str__(self):
        return "User: " + str(self.user) + " Evaluation: " + str(self.evaluacion)
        

class Evaluacion_Rubrica(models.Model):
    
    evaluacion = models.ForeignKey(Evaluacion,on_delete = models.CASCADE, null=True)
    rubrica = models.ForeignKey(Rubrica,on_delete = models.CASCADE, null=True)

    class Meta:
        unique_together = (("evaluacion","rubrica"),)

    def __str__(self):
        return "Evaluacion: " + str(self.evaluacion) + " Rubrica: " + str(self.rubrica)

class Cursos_Evaluacion(models.Model):
    
    curso = models.ForeignKey(Cursos,on_delete = models.CASCADE, null=True)
    evaluacion = models.ForeignKey(Evaluacion,on_delete = models.CASCADE, null=True)

    class Meta:
        unique_together = (("curso", "evaluacion"),)

    def __str__(self):
        return "Curso: " + str(self.curso) + " Evaluacion: " + str(self.evaluacion)

class Cursos_Alumnos(models.Model):
    
    nombreGrupo = models.CharField(max_length=50, null=True)
    curso = models.ForeignKey(Cursos, on_delete = models.CASCADE, null=True)
    alumnos = models.ForeignKey(Alumnos, on_delete = models.CASCADE, null=True)

    class Meta:
        unique_together = (("curso", "alumnos"),)

    def __str__(self):
        return self.nombre

class Alumnos_Evaluacion(models.Model):
    
    nota = models.FloatField(null=True)
    alumno = models.ForeignKey(Alumnos,on_delete=models.CASCADE, null=True)
    evaluacion = models.ForeignKey(Evaluacion,on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (("alumno","evaluacion"),)

    def __str__(self):
        return "Alumno: " + str(self.alumno) + " Nota: " + str(self.nota) + " Evaluacion: " + str(self.evaluacion)