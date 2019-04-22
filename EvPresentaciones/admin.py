from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Cursos)
admin.site.register(Alumnos)
admin.site.register(Rubrica)
admin.site.register(Usuario_Evaluacion)
admin.site.register(Evaluacion_Rubrica)
admin.site.register(Cursos_Evaluacion)
admin.site.register(Cursos_Alumnos)
admin.site.register(Alumnos_Evaluacion)