from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('galeria/', views.galeria, name='galeria'),
    path('reservas/', views.contacto, name='contacto'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_personalizado_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('eventos/', views.eventos, name='eventos'),
    path('api/eventos-externos/', views.EventosExternosAPIView.as_view(), name='api_eventos_externos'),
    path('api/consultas/', views.ConsultasAPIView.as_view(), name='api_consultas'),
    path('panel-admin/', views.dashboard_admin, name='dashboard'),
    path('panel-admin/editar/<int:pk>/', views.editar_consulta, name='editar_consulta'),
    path('panel-admin/eliminar/<int:pk>/', views.eliminar_consulta, name='eliminar_consulta'),
    path('panel-admin/cms/', views.cms_admin, name='cms_admin'),
]

