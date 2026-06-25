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
    path('eventos/', views.lista_eventos_api_view, name='eventos'),
    path('api/consultas/', views.ConsultasAPIView.as_view(), name='api_consultas')
]

