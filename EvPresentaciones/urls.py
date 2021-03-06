from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('testPage/<int:value>', views.testPage, name='testPage'),

    # Vistas de administrador

    path('Admin_interface/Cursos_admin',                    views.Cursos_admin,           name='cursos_admin'),
   # path('Admin_interface/Cursos_admin1',                    views.agregar_curso,         name='agregar_cursos'),
    path('Admin_interface/Evaluaciones_admin',              views.Evaluaciones_admin,     name='evaluaciones_admin'),
    path('Admin_interface/Evaluaciones_admin1',             views.agregar_evaluaciones,   name='agregar_evaluaciones'),
    path('Admin_interface/Evaluaciones_admin2/<int:id>',    views.eliminar_evaluaciones,  name='eliminar_evaluaciones'),
    path('Admin_interface/Evaluaciones_admin3/<int:id>',    views.modificar_evaluaciones, name='modificar_evaluaciones'),
    path('Admin_interface/evaluacion_admin/<int:id> <str:grupo>',       views.ver_evaluacion_admin,   name='ficha_evaluacion_admin'),
    path('Admin_interface/evaluacion_admin_1/<int:id>', views.cargar_grupo, name='cargar_grupo'),
    path('Admin_interface/evaluacion_agregar_evaluador/<int:id> <str:grupo>', views.evaluacion_agregar_evaluador, name='evaluacion_agregar_evaluador'),
    path('Admin_interface/Evaluadores_admin',               views.Evaluadores_admin,      name='evaluadores_admin'),
    path('Admin_interface/Landing_page_admin',              views.Landing_page_admin,     name='landing_page_admin'),
    path('Admin_interface/Rubricas_admin',                  views.Rubricas_admin,         name='rubricas_admin'),
    path('Admin_interface/Evaluadores_admin_1',             views.agregarEvaluador,       name='evaluadores_admin_agregar'),
    path('Admin_interface/Evaluadores_admin_2/<str:correo>',views.eliminarEvaluador,      name='evaluadores_admin_eliminar'),
    path('Admin_interface/Evaluadores_admin_3/<str:correo>',views.modificarEvaluador,     name='evaluadores_admin_modificar'),
    path('Admin_interface/ver_grupos/<int:id>',                             views.verGrupos,              name='ver_grupos'),
    path('Admin_interface/Ver_rubricas/<int:id>',                           views.ver_rubrica_select,     name='ver_select'),
    path('Admin_interface/Ver_rubrica_detalle/<str:nombre>/<str:version>',  views.ver_rubrica_detalle,    name='ver_detalle'),
    path('FichasRubricas/FichaRubrica_crear',                               views.Ficha_Rubrica_crear,    name='ficha_rubrica_crear'),
    path('FichasRubricas/FichaRubrica_eliminar/<str:nombre>/<str:version>', views.Ficha_Rubrica_eliminar, name='ficha_rubrica_eliminar'),
    path('FichasRubricas/FichaRubrica_modificar/<str:nombre>/<str:version>',views.Ficha_Rubrica_modificar,name='modificar_rubrica'),
    path('FichasRubricas/FichaRubrica_eliminar_definitivo/<str:nombre>/<str:version>/', views.Ficha_Rubrica_eliminar_definitivo, name='ficha_rubrica_eliminar_definitivo'),
    path('FichasRubricas/Rubrica_guardada',                                 views.guardarRubrica,         name='guardar_rubrica'),
    path('Admin_interface/postevalucionadmin',                              views.Post_evaluaciones_admin,name='post_evaluacion_admin'),
    path('Admin_interface/evaluacion_admin/<int:id><str:grupo>/<str:evaluador>', views.ver_evaluador_evaluacion, name='ver_evaluador_evaluacion'),
    path('Admin_interface/adminContacto.html',                              views.ContactoAdmin,          name='contactoAdmin'),
    path('Admin_interface/postevaluacionadmin',                             views.reset_grupo,            name='reset'),

    
    # Vistas de evaluador

    path('Eval_interface/langing_page_eval',                views.Laging_page_eval,       name='landing_page_eval'),
    path('Eval_interface/evaluacion/<int:id>',              views.ver_evaluacion_evaluador,             name='evaluacion'),
    path('Eval_interface/evaluacionesEvaluador',            views.Evaluaciones_eval,      name='evaluaciones_eval'),
    path('Eval_interface/postevaluacion',                   views.Post_evaluacion,        name='post_evaluacion'),
    path('FichasRubricas/FichaRubrica_crear',               views.Ficha_Rubrica_crear,    name='ficha_rubrica_crear'),
    path('FichasRubricas/FichaRubricaEvaluador',            views.Ficha_Rubrica_evaluador,name='ficha_rubrica_eval'),
    path('Summary_student/auth_summary',                    views.Auth_summary,           name='auth_summary'),
    path('Summary_student/summary',                         views.Summary,                name='summary'),
    path('LandingPage',                                     views.LandingPage,            name='LandingPage'),
    path('contactoEval',                                    views.ContactoEval,           name='contactoEval'),
    path('HomeAdmin',                                       views.HomeAdmin,              name='HomeAdmin')
]
