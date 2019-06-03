from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from .models import *
import csv
import random
import string
import os
from datetime import timedelta


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
    if not request.user.is_staff:
        return index(request)

    return render(request, 'EvPresentaciones/Admin_interface/Cursos_admin.html')


def Evaluaciones_admin(request):
    if not request.user.is_authenticated:
        return index(request)
    elif not request.user.is_staff:
        return index(request)

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

    # extraemos las rubricas que tienen evaluacion
    listaDeRubricasConEvaluaciones = []
    for er in ev_rub:
        listaDeRubricasConEvaluaciones.append(er.rubrica)

    # extraemos las rubricas que tienen evaluacion y las evaluaciones que tienen rubrica
    listaDeRubricasConEvaluaciones = []
    listaDeEvaluacionesConRubricas = []
    for er in ev_rub:
        listaDeRubricasConEvaluaciones.append(er.rubrica)
        listaDeEvaluacionesConRubricas.append(er.evaluacion)

    # annadimos a la lista solo las rubricas que no tienen evaluaciones
    restantes = []
    for r in rubricas:
        # solo si no se encuentra en las que tienen evaluacion asociada, la annadimos a la lista
        if r not in listaDeRubricasConEvaluaciones:
            restantes.append(r)

    return render(request, 'EvPresentaciones/Admin_interface/Evaluaciones_admin.html',
                  {'pareja': pareja, 'rubricas': rubricas, 'cursos': cursos, 'ev_rub': ev_rub,
                   'rub_restantes': restantes, 'EvsConRubrica': listaDeEvaluacionesConRubricas})


def eliminar_evaluaciones(request, id):
    """
    Vista que sirve para eliminar las evaluaciones cuando se presiona el boton eliminar en una rubrica.
    Solo deberia ser utilizada por el administrador.
    :param request:
    :return:
    """

    if not request.user.is_authenticated:
        return index(request)
    elif not request.user.is_staff:
        return index(request)

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

    print("Entro a vista modificar_evaluaciones")

    if not request.user.is_authenticated:
        return index(request)
    elif not request.user.is_staff:
        return index(request)

    # buscamos la evlaucion por su id
    evaluacion = Evaluacion.objects.get(id=id)

    # extraemos los datos del post
    fecha_inicio = request.POST.get('inicio', None)
    fecha_termino = request.POST.get('termino', None)
    estado = request.POST.get('estado', None)
    curso = request.POST.get('curso', None)
    rubrica = request.POST.get('rubricas', None)

    print(rubrica)

    # calculamos duracion a partir de la rubrica, Rubrica siempre va a existir en la base de datos
    rubricaObj = Rubrica.objects.get(id=rubrica)
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
    # por cada dato cambiamos el curso asociado
    for ce in cursos_evs:
        ce.curso = Cursos.objects.get(id=curso)
        ce.save()

    # retornamos a la pagina principal
    return Evaluaciones_admin(request)


def agregar_evaluaciones(request):
    """
    Vista que se ejecuta al annadir evaluaciones a la plataforma.
    """

    if not request.user.is_authenticated:
        return index(request)
    elif not request.user.is_staff:
        return index(request)

    # extraemos los datos del post
    fecha_inicio = request.POST.get('inicio', None)
    fecha_termino = request.POST.get('termino', None)
    estado = request.POST.get('estado', None)
    curso = request.POST.get('curso', None)
    rubrica = request.POST.get('rubricas', None)

    print(rubrica)

    # calculamos duracion a partir de la rubrica, Rubrica siempre va a existir en la base de datos
    rubricaObj = Rubrica.objects.get(id=rubrica)
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
    print(request.user)
    if not request.user.is_authenticated:
        return index(request)
    elif not request.user.is_staff:
        return index(request)

    # obtenemos numero de evaluadores
    try:
        evaluadores = Usuario.objects.all()
    except Usuario.DoesNotExist:
        evaluadores = []

    return render(request, 'EvPresentaciones/Admin_interface/Evaluadores_admin.html', {'evaluadores': evaluadores})


def Landing_page_admin(request):
    if not request.user.is_staff:
        return index(request)

    return render(request, 'EvPresentaciones/Admin_interface/Landing_page_admin.html')


# funciones Evaluaciones


def Evaluaciones(request):
    return render(request, 'EvPresentaciones/Eval_interface/evaluacion.html')


def Evaluacion_admin(request, ):
    return render(request, 'EvPresentaciones/Admin_interface/evaluacion_admin.html')


def Post_evaluacion(request):
    print("post Evaluacion")
    lineas = []
    grupo = request.POST.get('grupo', None)
    print(grupo)
    lista_atributos = request.POST.get('lista_atributos', None)
    idevaluacion = request.POST.get('idevaluacion', None)

    print(idevaluacion)

    evaluador = Usuario.objects.get(email=request.user)

    evaluacion = Cursos_Evaluacion.objects.get(evaluacion=idevaluacion)

    nombreArchivo = evaluacion.curso.codigo + '-' + evaluacion.curso.semestre + '.csv'
    rutaNombre = './EvPresentaciones/ArchivosEvaluaciones/' + nombreArchivo
    # manejo de string con las elecciones del evaluador
    lista_csv = []
    dict = {}

    lista_arreglada = lista_atributos.split("|")
    lista_arreglada = lista_arreglada[:-1]
    # crea diccionario para manejar
    for pareja in lista_arreglada:
        aux = pareja.split(":")
        dict[aux[0]] = aux[1]
    i = 0
    while i < len(dict.items()):
        aux = str(i + 1)
        lista_csv.append(dict[aux])
        i = i + 1

    nombre_evaluador = evaluador.first_name + " " + evaluador.last_name
    nombre_grupo = grupo
    nombre_evaluacion = str(idevaluacion)
    csvData = [nombre_evaluador, nombre_grupo, nombre_evaluacion, lista_csv]
    with open(rutaNombre, 'a', newline='') as csvFile:  # wb is wirte bytes
        writer = csv.writer(csvFile)
        writer.writerows([csvData])
    csvFile.close

    curso = evaluacion.curso.codigo + '-' + str(evaluacion.curso.seccion) + " " + evaluacion.curso.semestre + " " + str(
        evaluacion.curso.año)
    context = {}
    print(grupo)
    print(curso)
    print(idevaluacion)
    context['grupo'] = grupo
    context['curso'] = curso
    context['evaluacion'] = idevaluacion

    return render(request, 'EvPresentaciones/Eval_interface/postevaluacion.html',context)


def Post_evaluaciones_admin(request):
    lineas = []
    # todos los post
    lista_atributos = request.POST.get('lista_atributos', None)
    idevaluacion = request.POST.get('idevaluacion', None)
    minutos = request.POST.get('minutos', None)
    segundo = request.POST.get('segundos', None)
    presentador = request.POST.get('presentador', None)

    # todas las peticiones a la base de datos
    grupo = Cursos_Evaluacion.objects.get(evaluacion=idevaluacion)
    evaluador = Usuario.objects.get(email=request.user)
    rubrica = Evaluacion_Rubrica.objects.get(evaluacion=idevaluacion)
    evaluacion = Cursos_Evaluacion.objects.get(evaluacion=idevaluacion)
    grupo_integrantes = Cursos_Alumnos.objects.get(alumnos=presentador)
    grupo_integrantes = grupo_integrantes.nombreGrupo
    par_curso_integrantes = Cursos_Alumnos.objects.filter(nombreGrupo=grupo_integrantes)
    integrantes = []

    for i in par_curso_integrantes:
        integrantes.append(i.alumnos)
        i.evaluado = True
        i.save()
    for al in integrantes:
        aux = Alumnos_Evaluacion(tiempo=timedelta(minutes=int(minutos), seconds=int(segundo)), alumno=al,
                                 evaluacion=evaluacion.evaluacion)
        aux.save()

    # defino el nombre del archivo donde guardar
    nombreArchivo = evaluacion.curso.codigo + '-' + evaluacion.curso.semestre + '.csv'
    rutaNombre = './EvPresentaciones/ArchivosEvaluaciones/' + nombreArchivo

    # procesar archivo ingresado
    with open(rubrica.rubrica.archivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row != []:
                lineas.append(row)
    # criterios para poder sacar la descripcion de cada aspecto de la rubrica
    criterios = lineas.copy()
    escala = criterios.pop(0)
    escala.pop(0)

    alumno = Alumnos.objects.get(rut=presentador)
    alumno.presento = True
    alumno.save()

    # manejo de string con las elecciones del evaluador
    lista_csv = []
    dict = {}

    lista_arreglada = lista_atributos.split("|")
    lista_arreglada = lista_arreglada[:-1]
    # crea diccionario para manejar
    for pareja in lista_arreglada:
        aux = pareja.split(":")
        dict[aux[0]] = aux[1]
    i = 0
    while i < len(dict.items()):
        aux = str(i + 1)
        lista_csv.append(dict[aux])
        i = i + 1

    # creacion de csv
    nombre_evaluador = evaluador.first_name + " " + evaluador.last_name
    nombre_grupo = grupo.evaluando
    nombre_evaluacion = str(idevaluacion)
    csvData = [nombre_evaluador, nombre_grupo, nombre_evaluacion, lista_csv]
    with open(rutaNombre, 'a', newline='') as csvFile:  # wb is wirte bytes
        writer = csv.writer(csvFile)
        writer.writerows([csvData])
    csvFile.close
    # datos para mandar a la vista
    curso = evaluacion.curso.codigo + '-' + str(evaluacion.curso.seccion) + " " + evaluacion.curso.semestre + " " + str(
        evaluacion.curso.año)

    if grupo.evaluando == grupo_integrantes:
        estado = "Aún activa"
    else:
        estado = "Desactivada"
    context = {}
    context['grupo'] = grupo_integrantes
    context['curso'] = curso
    context['estado'] = estado
    context['evaluacion'] = idevaluacion

    return render(request,
                  'EvPresentaciones/Admin_interface/postevaluacionadmin.html', context)


def cargar_grupo(request, id):
    par_curso_evaluacion = Cursos_Evaluacion.objects.get(evaluacion=id)
    group = request.POST.get('grupo_enviado', None)
    par_curso_evaluacion.evaluando = group
    par_curso_evaluacion.save()

    return ver_evaluacion_admin(request, id)


def ver_evaluacion_evaluador(request, id):
    lineas = []
    alumnos = []
    aux = []
    par_curso_evaluacion = Cursos_Evaluacion.objects.get(evaluacion=id)
    par_evaluacion_rubrica = Evaluacion_Rubrica.objects.get(evaluacion=id)
    evaluacion = par_curso_evaluacion.evaluacion
    curso = par_curso_evaluacion.curso
    rubrica = par_evaluacion_rubrica.rubrica
    grupo = par_curso_evaluacion.evaluando
    # procesar archivo ingresado
    with open(rubrica.archivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row != []:
                lineas.append(row)
    # criterios para poder sacar la descripcion de cada aspecto de la rubrica
    criterios = lineas.copy()
    criterios.pop(0)
    # aspecto para guardar los encabezados de cada fila
    aspecto = []
    count = 0
    while count < len(criterios):
        lik = criterios[count]
        aspecto.append(lik[0])
        criterios[count].pop(0)
        count = count + 1
    data_curso = par_curso_evaluacion.curso.codigo + '-' + str(par_curso_evaluacion.curso.seccion) + " " + par_curso_evaluacion.curso.semestre + " " + str(
        par_curso_evaluacion.curso.año)
    context = {}
    context['aspecto'] = aspecto
    context['criterios'] = criterios
    context['grupo'] = grupo
    context['tamaño_atributos'] = len(aspecto)
    context['evaluacion'] =id
    context['curso'] = data_curso

    return render(request, 'EvPresentaciones/Eval_interface/evaluacion.html', context)


# Esta pagina recibe al grupo que estamos evaluando
def ver_evaluacion_admin(request, id, grupo):
    context = {}
    lineas = []
    alumnos = []
    aux = []

    par_curso_evaluacion = Cursos_Evaluacion.objects.get(evaluacion=id)
    par_evaluacion_rubrica = Evaluacion_Rubrica.objects.get(evaluacion=id)
    evaluacion = par_curso_evaluacion.evaluacion
    curso = par_curso_evaluacion.curso
    rubrica = par_evaluacion_rubrica.rubrica
    par_curso_evaluacion.evaluando = grupo
    par_curso_evaluacion.save()

    # falta que cambiemos a que el grupo este siendo evaluado
    grupo_elegido = grupo

    print("el grupo es: " + grupo_elegido)
    if grupo_elegido != "No Group":
        alumnos = Cursos_Alumnos.objects.filter(nombreGrupo=grupo_elegido)
    else:
        alumnos = []

    # Query para pedir alumnos del grupo en particular

    # para guardar objeto alumno y mandarlo
    sacar = 0
    while sacar < len(alumnos):
        par = alumnos[sacar]
        group = par.alumnos
        aux.append(group)
        sacar = sacar + 1

    # procesar archivo ingresado
    with open(rubrica.archivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row != []:
                lineas.append(row)

    # criterios para poder sacar la descripcion de cada aspecto de la rubrica
    criterios = lineas.copy()
    criterios.pop(0)
    # aspecto para guardar los encabezados de cada fila
    aspecto = []
    count = 0
    while count < len(criterios):
        lik = criterios[count]
        aspecto.append(lik[0])
        criterios[count].pop(0)
        count = count + 1

    #obtener la lista de evaluadores asociados a la evaluacion
    evaluadores = list()
    try:
        usuarios_evaluacion = Usuario_Evaluacion.objects.filter(evaluacion=id)
        for par in usuarios_evaluacion:
            # se agrega el objeto usuario
            evaluadores.append(Usuario.objects.get(email=par.user))

    except Usuario_Evaluacion.DoesNotExist:
        pass

    # lista de evaluadores que no estan en la evaluacion
    evaluadores_para_agregar = list()
    try:
        usuarios = Usuario.objects.all()
        #solo se pueden agregar usuarios que no estan agregados
        for evaluador in usuarios:
            if not (evaluador in evaluadores):
                evaluadores_para_agregar.append(evaluador)

    except Usuario.DoesNotExist:
        pass

    context['evaluacion'] = evaluacion
    context['curso'] = curso
    context['evaluadores'] = evaluadores
    context['evaluadores_para_agregar'] = evaluadores_para_agregar
    context['rubrica'] = lineas
    context['aspecto'] = aspecto
    context['criterios'] = criterios
    context['alumnos'] = aux
    context['grupo_elegido'] = grupo_elegido
    context['tamaño_atributos'] = len(aspecto)

    return render(request, 'EvPresentaciones/Admin_interface/evaluacion_admin.html',
                  context)


def evaluacion_agregar_evaluador(request, id, grupo):
    print(id)
    print(grupo)
    evaluacion = Evaluacion.objects.get(id=id)
    evaluador = Usuario.objects.get(email=request.POST.get('evaluador_agregado', None))
    par_evaluador_evaluacion = Usuario_Evaluacion(user=evaluador, evaluacion=evaluacion)
    par_evaluador_evaluacion.save()

    #evaluacion.save()
    print(evaluacion)
    #Usuario =
    print("agregar")
    #print(evaluador)
    return ver_evaluacion_admin(request, id, grupo)


def reset_grupo(request):
    evaluando = request.POST.get('reset', None)
    par_curso_evaluacion = Cursos_Evaluacion.objects.get(evaluacion=evaluando)
    par_curso_evaluacion.evaluando = "No Group"
    return Post_evaluaciones_admin(request)


# muestra los grupos que pueden ser evaluados, y los que ya fueron evaluados
def verGrupos(request, id):
    par_curso_evaluacion = Cursos_Evaluacion.objects.get(evaluacion=id)
    evaluacion = par_curso_evaluacion.evaluacion
    curso = par_curso_evaluacion.curso
    grupos_p = []
    grupos_e = []
    grupo = Cursos_Alumnos.objects.filter(curso=curso)
    for g in grupo:
        if (g.evaluado == False):
            if g.nombreGrupo not in grupos_p:
                grupos_p.append(g.nombreGrupo)
        else:
            if g.nombreGrupo not in grupos_e:
                grupos_e.append(g.nombreGrupo)

    return render(request, 'EvPresentaciones/Admin_interface/ver_grupos.html',
                  {'grupos_e': grupos_e, 'grupos_p': grupos_p, 'evaluacion': evaluacion})


# funciones resumen evaluacion


def Auth_summary(request):
    return render(request, 'EvPresentaciones/Summary_student/auth_summary.html')


def Summary(request):
    return render(request, 'EvPresentaciones/Summary_student/summary.html')


# Se hace así porque hay que sacar la rúbrica del modelo Evaluacion_Rubrica, no es directo
def ver_rubrica_select(request, id):
    rubrica = Evaluacion_Rubrica.objects.get(evaluacion=id).rubrica
    return ver_rubrica_detalle(request, rubrica.nombre, rubrica.version)


# Si se hace request de la landingpage, se verifica el tipo de usuario y se retorna el render correspondiente
def LandingPage(request):
    email = request.POST.get('username', None)  # Get data from POST
    passw = request.POST.get('password', None)
    user = authenticate(request, email=email, password=passw)
    if user is not None:
        login(request, user)
        if request.user.is_staff:
            return render(request, 'EvPresentaciones/Admin_interface/Landing_page_admin.html')
        else:
            return render(request, 'EvPresentaciones/Eval_interface/Landing_page_eval.html')

    return index(request, True)


def HomeAdmin(request):
    return render(request, 'EvPresentaciones/Admin_interface/Landing_page_admin.html')


def eliminarEvaluador(request, correo):
    """Elimina el evaluador asociado a un correo"""

    if request.user.email == correo:
        messages.error(request, 'Error: No es posible eliminarse a sí mismo de la lista de evaluadores',
                       extra_tags='w3-panel w3-red')
        return Evaluadores_admin(request)

    # eliminamos usuario con el id que se nos entrego
    Usuario.objects.get(email=correo).delete()

    messages.success(request,
                     'Operación realizada: se ha eliminado al usuario ' + correo + ' de la lista de evalauadores',
                     extra_tags='w3-panel w3-green')

    return Evaluadores_admin(request)


def modificarEvaluador(request, correo):
    """Modifica el evaludor asociado un correo"""

    nuevo_nombre = request.POST.get('usrname', None)
    nuevo_apellido = request.POST.get('apellido', None)
    nuevo_correo = request.POST.get('correo', None)

    try:
        evaluador = Usuario.objects.get(email=correo)
        evaluador.first_name = nuevo_nombre
        evaluador.last_name = nuevo_apellido
        evaluador.email = nuevo_correo
        evaluador.save()
        messages.success(request, "Evaluación modificada con éxito. Nombre: " + nuevo_nombre + ', Apellido: '
                         + nuevo_apellido + ', email: ' + nuevo_correo, extra_tags='w3-panel w3-green')

    except Usuario.DoesNotExist:
        messages.error(request, 'Error: El evaluador que intenta modificar no existe', extra_tags='w3-panel w3-red')

    except IntegrityError:
        messages.error(request, 'Error: Existe otro evaluador asociado al correo ' + nuevo_correo,
                       extra_tags='w3-panel w3-red')

    return Evaluadores_admin(request)


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def agregarEvaluador(request):
    """Agrega un evaluador con el nombre, apellido y correo entregados"""

    nombre = request.POST.get('usrname', None)
    apellido = request.POST.get('apellido', None)
    correo = request.POST.get('correo', None)
    contraseña = randomString(25)

    try:
        Usuario.objects.create_user(email=correo, first_name=nombre, last_name=apellido, password=contraseña)
        messages.success(request,
                         "Evaluador creado con éxito: Nombre: " + nombre + ', Apellido: ' + apellido + ', email: ' + correo,
                         extra_tags='w3-panel w3-green')

    except IntegrityError:
        messages.error(request, 'Error: Ya existe un usuario asociado al correo ' + correo,
                       extra_tags='w3-panel w3-red')

    return Evaluadores_admin(request)


def Laging_page_eval(request):
    return render(request, 'EvPresentaciones/Eval_interface/Landing_page_eval.html')


# Funcion para la vista para los evaluadores
def Evaluaciones_eval(request):
    # diccionario para guardar la informacion que devolveremos
    context = {}
    # consigo informacion de la sesion
    evaluador = request.user.id
    # saco objetos de la base de datos ordenados
    par = Evaluacion.objects.filter(usuario_evaluacion__user=evaluador).order_by('-fechaInicio')[:10]
    curso_eval = Cursos_Evaluacion.objects.all()
    # guardo en diccionario
    context['par'] = par
    context['cursos'] = curso_eval
    return render(request, 'EvPresentaciones/Eval_interface/evaluacionesEvaluador.html', context)


def Evaluaciones_Curso(request):
    context = {}
    return render(request, 'EvPresentaciones/Eval_interface/evaluacionesCurso.html', context)


######### RÚBRICAS #######

# Landing page de rúbricas del administrador
def Rubricas_admin(request):
    rubricas = Rubrica.objects.all()
    # listaDeAspectos = []
    listaIDs = []
    listaNombres = []
    listaVersiones = []
    listaArchivos = []

    for rubrica in rubricas:  # Para todas las rúbricas
        listaIDs.append(int(rubrica.id))
        listaNombres.append(str(rubrica.nombre))
        listaVersiones.append(str(rubrica.version))
        listaArchivos.append(str(rubrica.archivo))

        # sacar los aspectos del archivo en csv
        # aspectos = []

        # lineas = [] # tiene todas las filas
        # procesar archivo ingresado
        # with open(rubrica.archivo) as csv_file:
        #    csv_reader = csv.reader(csv_file, delimiter=',')
        #    for row in csv_reader:
        #        lineas.append(row)
        #        print(row)
        #
        # for r in lineas[1:-1]:
        #    aspectos.append(r[0]) # Saca la primera columna de la rubrica
        #    print(r[0])
        #
        # listaDeAspectos.append(aspectos) # Es una fila con todos los aspectos
        # print(listaDeAspectos)

    listaEntregada = []
    for i in range(len(listaNombres)):
        # añadir el indice al final porque template es rarito y no acepta colocar id strings.
        listaEntregada.append([listaIDs[i], listaNombres[i], listaVersiones[i],
                               listaArchivos[i]])  # Le paso el indice para poder usarlo de id en elementos html
    print(listaEntregada)

    return render(request, 'EvPresentaciones/Admin_interface/Rubricas_admin.html', {'lista': listaEntregada})


def Ficha_Rubrica_evaluador(request):
    return render(request, 'EvPresentaciones/FichasRubricas/FichaRubricaEvaluador.html')


def ver_rubrica_detalle(request, nombre, version):
    rubrica = Rubrica.objects.get(nombre=nombre, version=version)
    # Filas
    lineas = []
    # procesar archivo ingresado
    with open(rubrica.archivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='$')  # Para que el texto pueda tener ','
        for row in csv_reader:
            lineas.append(row)

    # Tiempo en formato simplificado
    tiempoMax = str(rubrica.tiempo).split(":")
    tMax = tiempoMax[1] + ":" + tiempoMax[2]  # Tiempo en formato correcto: mm:ss
    tiempoMin = str(rubrica.tiempoMin).split(":")
    tMin = tiempoMin[1] + ":" + tiempoMin[2]  # Tiempo en formato correcto: mm:ss

    return render(request, 'EvPresentaciones/Admin_interface/ver_rubrica_detalle.html',
                  {'lineas': lineas, 'tmax': tMax, 'tmin': tMin})


def Ficha_Rubrica_modificar(request, nombre, version):
    rubrica = Rubrica.objects.get(nombre=nombre, version=version)
    # Extraer contenido
    rows = []
    with open(rubrica.archivo) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='$')  # Para tener ',' dentro de los campos
        for row in csv_reader:
            rows.append(row)

    # Código para quitar lineas en blanco
    rows2 = []
    for r in rows:
        if r != []:  # Sólo si no es vacío
            rows2.append(r)  # Se agrega

    # Movemos las filas no balncas
    rows = rows2
    primeraFila = rows[0][1:]  # Quito el primer y ultimo elemento que son elementos vacios no editables
    contenido = rows[1:]
    tiempoMax = str(rubrica.tiempo).split(":")
    tMax = tiempoMax[1] + ":" + tiempoMax[2]  # Tiempo en formato correcto: mm:ss
    tiempoMin = str(rubrica.tiempoMin).split(":")
    tMin = tiempoMin[1] + ":" + tiempoMin[2]  # Tiempo en formato correcto: mm:ss

    return render(request, 'EvPresentaciones/FichasRubricas/FichaRubrica_modificar.html',
                  {'nombre': rubrica.nombre, 'version': rubrica.version, 'tiempo': tMax,
                   'tiempoMin': tMin, 'primeraFila': primeraFila, 'contenido': contenido})


# Sólo para admin, permite crear rúbricas desde 0
def Ficha_Rubrica_crear(request):
    return render(request, 'EvPresentaciones/FichasRubricas/FichaRubrica_crear.html')


def Ficha_Rubrica_eliminar(request, nombre, version):
    rubrica = Rubrica.objects.get(nombre=nombre, version=version)
    rubricaID = rubrica.id
    # print(rubricaID)
    evaluacionesAsociadas = Evaluacion_Rubrica.objects.filter(rubrica=rubricaID)
    evaluacionesSTR = []
    evaluacionesIDs = []  # Para obtener cursos asociados a evaluaciones
    for e in evaluacionesAsociadas:
        evaluacionesSTR.append(str(e.evaluacion))
        evaluacionesIDs.append(e.id)
    # print(evaluacionesSTR)
    evaluacionesSTR = list(dict.fromkeys(evaluacionesSTR))  # Saca duplicados
    cursosAsociados = []  # LISTA DE OBJETOS TIPO CURSO
    for i in range(len(evaluacionesIDs)):
        cursosAsociados.append(
            str(Cursos_Evaluacion.objects.get(evaluacion=evaluacionesIDs[i]).curso))  # Extraigo id de cursos asociados
    cursosAsociados = list(dict.fromkeys(cursosAsociados))  # Saca duplicados
    return render(request, 'EvPresentaciones/FichasRubricas/FichaRubrica_eliminar.html',
                  {'evaluaciones': evaluacionesSTR, 'cursos': cursosAsociados, 'nombre': nombre, 'version': version})


def Ficha_Rubrica_eliminar_definitivo(request, nombre, version):
    rubrica = Rubrica.objects.get(nombre=nombre, version=version)
    archivo = rubrica.archivo

    # Aquí eliminar fila de Evaluacion_Rubrica
    rubrica = Rubrica.objects.get(nombre=nombre, version=version)
    rubricaID = rubrica.id
    evaluacionesAsociadas = Evaluacion_Rubrica.objects.filter(rubrica=rubricaID)
    evaluacionesIDs = []  # Para obtener cursos asociados a evaluaciones
    for e in evaluacionesAsociadas:
        evaluacionesIDs.append(e.id)
    evaluacion_rubrica_Asociadas = []
    for id in evaluacionesIDs:
        evaluacion_rubrica_Asociadas = Evaluacion_Rubrica.objects.filter(id=id)

    for evaluacion_rubrica in evaluacion_rubrica_Asociadas:
        evaluacion_rubrica.remove()

    # Aquí eliminar rúbrica en su modelo
    rubrica.delete()

    # Aquí eliminar archivo
    os.remove(archivo)
    return render(request, 'EvPresentaciones/FichasRubricas/FichaRubrica_eliminar_definitivo.html',
                  {'nombre': nombre, 'version': version})


# Request genérico que guarda o sobreescribe una rúbrica
def guardarRubrica(request):
    nombre = request.POST.get('nombre-rubrica', None)
    tmin = request.POST.get('t-min', None)
    tmax = request.POST.get('t-max', None)
    version = request.POST.get('version', None)
    rubrica = request.POST.get('csv-text', None)  # Aquí viene la rúbrica completa
    rows = rubrica.split("|")

    # Nombre de archivo
    nombreArchivo = nombre + '-' + version + '.csv'
    rutaNombre = './EvPresentaciones/ArchivosRubricas/' + nombreArchivo

    # Tener el formato solicitado para guardar
    csvData = []
    for row in rows:
        csvData.append(row.split('$'))  # para tener ',' en textos
    print(csvData)
    # No se revalida el requisito 51, ya que la implementación en frontend es sólida.
    # Además existen otras prioridades de desarrollo.

    # Guardar el archivo como csv, se sobreescribe si tiene el mismo nombre
    with open(rutaNombre, 'w') as csvFile:  # wb is wirte bytes
        writer = csv.writer(csvFile, delimiter='$')  # para tener ',' en textos
        writer.writerows(csvData)
    csvFile.close

    # Guardar en la base de datos
    # try:
    tminn = tmin.split(':')  # Extraer los minutos y segundos
    tmaxx = tmax.split(':')

    # Nos abrimos al caso en que solo haya colocado segundos
    if len(tminn) == 1:
        tminn2 = [0, tminn[0]]
        tminn = tminn2

    if len(tmaxx) == 1:
        tmaxx2 = [0, tmaxx[0]]
        tmaxx = tmaxx2

    # Aquí modificar los parametros de una existente, o crear una nueva
    try:
        r = Rubrica.objects.get(nombre=nombre, version=version)
        r.tiempo = timedelta(minutes=int(tmaxx[0]), seconds=int(tmaxx[1]))
        r.tiempoMin = timedelta(minutes=int(tminn[0]), seconds=int(tminn[1]))
    except Rubrica.DoesNotExist:
        Rubrica.create_rubrica(nombre=nombre, tiempoMin=timedelta(minutes=int(tminn[0]), seconds=int(tminn[1])),
                               tiempoMax=timedelta(minutes=int(tmaxx[0]), seconds=int(tmaxx[1])), version=version,
                               archivo=rutaNombre)
    # except IntegrityError:
    #    messages.error(request, 'Error: Ya existe la rúbrica ' + nombre+'-'+version, extra_tags='w3-panel w3-red')
    return render(request, 'EvPresentaciones/FichasRubricas/Rubrica_guardada.html')
