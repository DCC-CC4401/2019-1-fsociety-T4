from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser


class UsuarioManager(BaseUserManager):
    """
    Aquí van las funciones para crear usuarios, se pueden agregar para personalizar aun mas el usuario creado
    """

    def create_user(self, email, first_name, last_name, password=None):
        """
        Crea un usuario que no es staff ni superuser
        """
        if not email:
            raise ValueError('Users must have an email address')

        print(self.model)

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.username = email
        user.save(using=self._db)
        return user




    def create_superuser(self, email, first_name, last_name, password):
        """
        Crea un superuser
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.is_superuser = True
        user.is_staff= True
        user.save(using=self._db)
        return user


# Create your models here.

# Tablas de la base de datos
class Usuario(AbstractUser):
    """
    Clase Usuario: esta clase representa los usuarios dentro del sistema.
    Hereda los atributos del a clase Users de Django.

    Atributos:
    email: correo electrónico (llave)
    first_name: nombre
    last_name: apellido
    is_staff: True si es administraor
    is_superuser: True si es superusuario
    is_active: True si esta activo (en vez de borrar usuarios se desactivan)
    date_joined = fecha de creacion
    """

    # ahora no es necesario username para autenticarse, este campo es seteado al emai, pero no deberia usarse
    AbstractUser._meta.get_field('username')._unique = False

    # nueva llave del usuario
    email = models.EmailField(unique=True)

    # indica que el email es la llave
    USERNAME_FIELD = 'email'

    # no pide ningún otro dato adicional para crear un usuario (solo email y pass)
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # se asocia la clase constructora
    objects = UsuarioManager()


    # Para linkear las tablas
    class Meta:
        db_table = "Usuario"

    def __str__(self):
        # definir como ver las filas de la tabla
        return self.email

    def isAdmin(self):
        # retorna si es admin o no
        return self.is_staff


class Cursos(models.Model):
    # id automatico sera la llave
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    semestre = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    seccion = models.PositiveIntegerField()

    class Meta:
        db_table = "Cursos"
        unique_together = (("codigo", "semestre", "año", "seccion"),)

    def __str__(self):
        # asi se despliega en la ficha de evaluacion
        return self.codigo + "-" + str(self.seccion) + "/" + self.semestre + "/" + str(self.año)


class Alumnos(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    presento = models.BooleanField()
    rut = models.PositiveIntegerField(primary_key=True)
    codigoVerificador = models.CharField(max_length=1)

    class Meta:
        db_table = "Alumnos"

    def __str__(self):
        return str(self.rut) + "-" + str(self.codigoVerificador)


class Rubrica(models.Model):
    # id es automatico
    nombre = models.CharField(max_length=50)
    version = models.CharField(max_length=50)
    tiempo = models.DurationField() # tiempoMax
    tiempoMin = models.DurationField(default=0)
    archivo = models.FilePathField(path='./EvPresentaciones/ArchivosRubricas', default="./")

    class Meta:
        db_table = "Rubrica"

    def __str__(self):
        return self.nombre + " v" + self.version
    
    def create_rubrica(nombre, tiempoMin, tiempoMax, version, archivo):
        r = Rubrica(
            nombre=nombre,
            tiempoMin=tiempoMin,
            tiempo=tiempoMax,
            version=version,
            archivo = archivo
        )
        r.save()
        return r


class Evaluacion(models.Model):
    # id es automatico
    fechaInicio = models.DateField()
    fechaTermino = models.DateField()
    estado = models.CharField(max_length=50)
    duracion = models.DurationField()

    class Meta:
        db_table = "Evaluacion"

    def __str__(self):
        return "ID: " + str(self.id) + " | Inicio: " + str(self.fechaInicio) + " | Término: " + str(self.fechaTermino) + " | Estado: " + str(self.estado)


##############################################################
# Tablas conectoras

class Usuario_Evaluacion(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, null=True)


    class Meta:
        unique_together = (("user", "evaluacion"),)

    def __str__(self):
        return "User: " + str(self.user) + " Evaluation: " + str(self.evaluacion)

    def getUser(self):
        return self.user

    def getEvaluacion(self):
        return self.evaluacion



class Evaluacion_Rubrica(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, null=True)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (("evaluacion", "rubrica"),)

    def __str__(self):
        return "Evaluacion: (" + str(self.evaluacion) + ")     Rúbrica: (" + str(self.rubrica) + ")"


class Cursos_Evaluacion(models.Model):
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE, null=True)
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (("curso", "evaluacion"),)

    def __str__(self):
        return "Curso: " + str(self.curso) + " Evaluacion: " + str(self.evaluacion)


class Cursos_Alumnos(models.Model):
    nombreGrupo = models.CharField(max_length=50, null=True, default="No Group")
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE, null=True)
    alumnos = models.ForeignKey(Alumnos, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (("curso", "alumnos"),)

    def __str__(self):
        return self.nombreGrupo


class Alumnos_Evaluacion(models.Model):
    nota = models.FloatField(null=True)
    tiempo = models.DurationField(default=0)  # tiempo de la evaluacion
    alumno = models.ForeignKey(Alumnos, on_delete=models.CASCADE, null=True)
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return "Alumno: " + str(self.alumno) + " Nota: " + str(self.nota) + " Evaluacion: " + str(self.evaluacion)
