from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import csv
import random
import string


# Create your views here.


def index(request, valor=False):
    return render(request, 'EvPresentaciones/Index.html', {'value': valor})


def testPage(request, value):
    """
    Pagina de prueba de la aplicacion.
    se ingresa a ella con /EvPresenataciones/testPage/0 o con /EvPresenataciones/testPage/1    
    """

    # Retornamos el el request, con el html asociado y un diccionario con los parametros que este necesita.
    return render(request, 'EvPresentaciones/testPage.html', {'value': value, 'list': range(1, value)})


# funciones Admin interface


def Cursos_admin(request):
    return render(request, 'EvPresentaciones/Admin_interface/Cursos_admin.html')


def Evaluaciones_admin(request):
    # obtenemos las evaluaciones y los cursos
    pareja = Cursos_Evaluacion.objects.all()

    # Datos para agregar nuevas evaluaciones
    try:
        rubricas = Rubrica.objects.all()
    except Rubrica.DoesNotExist:
        rubricas = []

    try:
        cursos = Cursos.objects.all()
    except Cursos.DoesNotExist:
        cursos = []

    # extraemos evaluaciones y rubricas para mostrar y modificar las cosas ya existentes
    try:
        ev_rub = Evaluacion_Rubrica.objects.all()
    except Evaluacion_Rubrica.DoesNotExist:
        ev_rub = []

    # extraemos rubricas que no se encuentran en ev_rub para el html

    #extraemos las rubricas que tienen evaluacion
    listaDeRubricasConEvaluaciones = []
    for er in ev_rub:
        listaDeRubricasConEvaluaciones.append(er.rubrica)

    #annadimos a la lista solo las rubricas que no tienen evaluaciones
    restantes = []
    for r in rubricas:
        #solo si no se encuentra en las que tienen evaluacion asociada, la annadimos a la lista
        if r not in listaDeRubricasConEvaluaciones:
            restantes.append(r)

    return render(request, 'EvPresentaciones/Admin_interface/Evaluaciones_admin.html',
                  {'pareja': pareja, 'rubricas': rubricas, 'cursos': cursos, 'ev_rub': ev_rub, 'rub_restantes':restantes})


def eliminar_evaluaciones(request, id):
    """
    Vista que sirve para eliminar las evaluaciones cuando se presiona el boton eliminar en una rubrica.
    Solo deberia ser utilizada por el administrador.
    :param request:
    :return:
    """

    # Eliminamos evaluacion por el id
    Evaluacion.objects.get(id=id).delete()

    # hay que borrar de todas las otras tablas en donde se guarde relacion.
    Usuario_Evaluacion.objects.filter(evaluacion_id=id).delete()
    Evaluacion_Rubrica.objects.filter(evaluacion_id=id).delete()
    Cursos_Evaluacion.objects.filter(evaluacion_id=id).delete()
    Alumnos_Evaluacion.objects.filter(evaluacion_id=id).delete()

    # mensaje de debuggeo.
    print("borrado:" + str(id))

    # regresamos a la pagina normalmente
    return Evaluaciones_admin(request)


def modificar_evaluaciones(request, id):
    """
    Vista que se ejecuta al modifcar una evaluacion
    """

    # buscamos la evlaucion por su id
    evaluacion = Evaluacion.objects.get(id=id)

    # extraemos los datos del post
    fecha_inicio = request.POST.get('inicio', None)
    fecha_termino = request.POST.get('termino', None)
    estado = request.POST.get('estado', None)
    curso = request.POST.get('curso', None)
    rubrica = request.POST.get('rubricas', None)

    # calculamos duracion a partir de la rubrica, Rubrica siempre va a existir en la base de datos
    rubricaObj = Rubrica.objects.get(nombre=rubrica)
    tMax = rubricaObj.tiempo

    # cambiamos los datos de la evaluacion
    evaluacion.fechaInicio = fecha_inicio
    evaluacion.fechaTermino = fecha_termino
    evaluacion.estado = estado
    evaluacion.duracion = tMax

    evaluacion.save()

    # hay que cambiar la rubrica  y los cursos asociados tambien

    # rubrica-evaluacion
    # extraemos de la tabla los datos que tengan la evaluacion asociada
    eb_rubs = Evaluacion_Rubrica.objects.filter(evaluacion=evaluacion)
    # por cada dato de la evaluacion asociada cambiamos su rubrica a la pedida
    for er in eb_rubs:
        er.rubrica = rubricaObj
        er.save()

    # curso-evaluacion
    # extraemos de la tabla los cursos que tengan la evaluacion asociada
    cursos_evs = Cursos_Evaluacion.objects.filter(evaluacion=evaluacion)
    #por cada dato cambiamos el curso asociado
    for ce in cursos_evs:
        ce.curso = Cursos.objects.get(id=curso)
        ce.save()

    #retornamos a la pagina principal
    return Evaluaciones_admin(request)


def agregar_evaluaciones(request):
    """
    Vista que se ejecuta al annadir evaluaciones a la plataforma.
    """

    # extraemos los datos del post
    fecha_inicio = request.POST.get('inicio', None)
    fecha_termino = request.POST.get('termino', None)
    estado = request.POST.get('estado', None)
    curso = request.POST.get('curso', None)
    rubrica = request.POST.get('rubricas', None)

    # calculamos duracion a partir de la rubrica, Rubrica siempre va a existir en la base de datos
    rubricaObj = Rubrica.objects.get(nombre=rubrica)
    tMax = rubricaObj.tiempo

    # añadimos la evaluacion a las tablas correspondientes
    evaluacion = Evaluacion(fechaInicio=fecha_inicio,
                            fechaTermino=fecha_termino,
                            estado=estado,
                            duracion=tMax)
    evaluacion.save()

    # evaluacion-rubrica
    ev_rub = Evaluacion_Rubrica(evaluacion=evaluacion,
                                rubrica=rubricaObj)
    ev_rub.save()

    # curso-evaluacion
    cur_ev = Cursos_Evaluacion(curso_id=curso,
                               evaluacion=evaluacion)
    cur_ev.save()

    # hay que añadirle a cada alumno del curso la evaluacion
    try:
        alumnos = Cursos_Alumnos.objects.filter(curso_id=curso)

    except Cursos_Alumnos.DoesNotExist:
        alumnos = []

    for alum in alumnos:
        alum_ev = Alumnos_Evaluacion(alumno=alum.alumnos,
                                     evaluacion=evaluacion)
        alum_ev.save()

    return Evaluaciones_admin(request)


def Evaluadores_admin(request):
    # obtenemos numero de evaluadores
    try:
        evaluadores = Usuario.objects.all()
    except Usuario.DoesNotExist:
        evaluadores = []

    return render(request, 'EvPresentaciones/Admin_interface/Evaluadores_admin.html', {'evaluadores': evaluadores})


def Landing_page_admin(request):
    return render(request, 'EvPresentaciones/Admin_interface/Landing_page_admin.html')


def Rubricas_admin(request):
    rubricas = Rubrica.objects.all()
    listaDeAspectos = []
    listaNombres = []

    for rubrica in rubricas:
        listaNombres.append(str(rubrica.nombre))

        # sacar los aspectos del archivo en csv
        aspectos = []

        lineas = []
        # procesar archivo ingresado
        with open(rubrica.archivo) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                lineas.append(row)

        for r in lineas[1:-1]:
            aspectos.append(r[0])

        listaDeAspectos.append(aspectos)

    listaEntregada = []
    for i in range(len(listaNombres)):
        # añadir el indice al final porque template es rarito y no acepta colocar id strings.
        listaEntregada.append([listaNombres[i], listaDeAspectos[i], i])

    return render(request, 'EvPresentaciones/Admin_interface/Rubricas_admin.html', {'lista': listaEntregada})


# funciones Evaluaciones


def Evaluaciones(request):
    return render(request, 'EvPresentaciones/Eval_interface/evaluacion.html')


def Evaluacion_admin(request):
    return render(request, 'EvPresentaciones/Eval_interface/evaluacionadmin.html')


def Post_evaluacion(request):
    return render(request, 'EvPresentaciones/Eval_interface/postevaluacion.html')


def Post_evaluaciones_admin(request):
    return render(request, 'EvPresentaciones/Eval_interface/postevaluacionadmin.html')


# funciones Rubricas

# ficha en donde los administradores crean nuevas rubricas
def Ficha_Rubrica_admin(request):
    return render(request, 'EvPresentaciones/FichasRubricas/FichaRubricaAdministrador.html')


def Ficha_Rubrica_evaluador(request):
    return render(request, 'EvPresentaciones/FichasRubricas/FichaRubricaEvaluador.html')


# funciones resumen evaluacion


def Auth_summary(request):
    return render(request, 'EvPresentaciones/Summary_student/auth_summary.html')


def Summary(request):
    return render(request, 'EvPresentaciones/Summary_student/summary.html')


def ver_rubrica_select(request, id):
    rubrica = Evaluacion_Rubrica.objects.get(evaluacion=id)

    # sacar los aspectos del archivo en csv
    aspectos = []

    lineas = []
    # procesar archivo ingresado
    with open(rubrica.rubrica.archivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            lineas.append(row)

    for r in lineas[1:-1]:
        aspectos.append(r[0])

    return render(request, 'EvPresentaciones/Admin_interface/ver_rubrica_select.html',
                  {'rubrica': rubrica.rubrica.nombre, 'aspectos': aspectos})


# Si se hace request de la landingpage, se verifica el tipo de usuario y se retorna el render correspondiente
def LandingPage(request):
    user = request.POST.get('username', None)  # Get data from POST
    passw = request.POST.get('password', None)

    try:
        username = Usuario.objects.get(correo=user, contrasena=passw)

    except Usuario.DoesNotExist:
        return index(request, True)
    #Guardamos en la sesion los valores de usuario para futuros usos.
    request.session['user_name']=user

    # Si llegamos aquí el usuario ya se autenticó
    if username.isAdmin():
        return render(request, 'EvPresentaciones/Admin_interface/Landing_page_admin.html')
    else:
        return render(request, 'EvPresentaciones/Eval_interface/Landing_page_eval.html')


def HomeAdmin(request):
    return render(request, 'EvPresentaciones/Admin_interface/Landing_page_admin.html')


def eliminarEvaluador(request, correo):
    if not

    # eliminamos usuario con el id que se nos entrego
    Usuario.objects.get(correo=correo).delete()

    return Evaluadores_admin(request)

def modificarEvaluador(request, correo):
    # eliminamos usuario con el id que se nos entrego
    eliminarEvaluador(request, correo)

    return agregarEvaluador(request)


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def agregarEvaluador(request):
    nombre = request.POST.get('usrname', None)
    apellido = request.POST.get('apellido', None)
    correo = request.POST.get('correo', None)

    contraseña = randomString(25)

    usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo,
                      contrasena=contraseña, esAdministrador=False)
    usuario.save()

    return Evaluadores_admin(request)


def ver_rubrica_detalle(request, nombre):
    rubrica = Rubrica.objects.get(nombre=nombre)

    lineas = []
    # procesar archivo ingresado
    with open(rubrica.archivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            lineas.append(row)

    tmax = lineas[-1][2]
    tmin = lineas[-1][1]

    lineas[0][0] = ''
    lineas = lineas[:-1]

    return render(request, 'EvPresentaciones/Admin_interface/ver_rubrica_detalle.html',
                  {'lineas': lineas, 'tmax': tmax, 'tmin': tmin})


def Laging_page_eval(request):
    return render(request, 'EvPresentaciones/Eval_interface/Landing_page_eval.html')


# Funcion para la vista para los evaluadores
def Evaluaciones_eval(request):
    #diccionario para guardar la informacion que devolveremos
    context={}
    #consigo informacion de la sesion
    evaluador= request.session['user_name']
    #saco objetos de la base de datos ordenados
    par= Evaluacion.objects.filter(usuario_evaluacion__user=evaluador).order_by('-fechaInicio')[:10]
    curso_eval= Cursos_Evaluacion.objects.all()
    #guardo en diccionario
    context['par']=par
    context['cursos']= curso_eval
    return render(request, 'EvPresentaciones/Eval_interface/evaluacionesEvaluador.html',context)

def Evaluaciones_Curso(request):
    context={}
    return render(request,'EvPresentaciones/Eval_interface/evaluacionesCurso.html',context)