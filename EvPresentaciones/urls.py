from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('testPage/<int:value>', views.testPage, name='testPage'),
]