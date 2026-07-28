from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from .forms import ContactoForm, RegistroDatosBasicosForm, ValidacionCodigoForm, ContenidoInicioForm
from .models import SolicitudConsulta, UsuarioPermitido, ContenidoInicio
from .serializers import SolicitudConsultaSerializer


# --- Vistas Principales del Sitio ---

def inicio(request):
    contenido, _ = ContenidoInicio.objects.get_or_create(id=1)
    return render(request, 'mi_app/inicio.html', {'contenido': contenido})

imagenes = [
    {'url': 'imagenes/party.jpg'},
    {'url': 'imagenes/party2.jpg'},
    {'url': 'imagenes/party3.jpg'},
    {'url': 'imagenes/party4.jpg'},
    {'url': 'imagenes/party5.jpg'},
    {'url': 'imagenes/party6.jpg'},
    {'url': 'imagenes/party7.jpg'},
    {'url': 'imagenes/party8.jpg'},
    {'url': 'imagenes/party9.jpg'},
    {'url': 'imagenes/party10.jpg'},
    {'url': 'imagenes/party9.jpg'},
    {'url': 'imagenes/party8.jpg'},
    {'url': 'imagenes/party7.jpg'},
    {'url': 'imagenes/party6.jpg'},
    {'url': 'imagenes/party5.jpg'},
    {'url': 'imagenes/party4.jpg'},
    {'url': 'imagenes/party3.jpg'},
    {'url': 'imagenes/party2.jpg'},
    {'url': 'imagenes/party.jpg'},
]

def galeria(request):
    return render(request, 'mi_app/galeria.html', {'lista_imagenes': imagenes})

def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)

        if form.is_valid():
            nueva_solicitud = form.save()
            categoria_actual = nueva_solicitud.categoria_asignada
            cuerpo_mensaje = f"""
                    Hola Anna,

                    Se ha registrado una nueva solicitud en la web de Eclipse Night Club.
                    A continuación, te detallamos los datos cargados por el usuario:

                    --------------------------------------------------
                    Categoría Clasificada: {categoria_actual}
                    Nombre Completo: {form.cleaned_data.get('nombre_completo')}
                    Correo del Cliente: {form.cleaned_data.get('correo_electronico')}
                    Fecha Solicitada: {form.cleaned_data.get('fecha_reserva') if form.cleaned_data.get('fecha_reserva') else 'No aplica'}
                    Cantidad de Personas: {form.cleaned_data.get('cantidad_personas') if form.cleaned_data.get('cantidad_personas') else 'No aplica'}
                    Mensaje / Consulta:
                    {form.cleaned_data.get('mensaje')}
                    --------------------------------------------------

                    Este registro ya se encuentra almacenado de forma segura en PostgreSQL.
                    """
            asunto = f"Nueva Solicitud Recibida — Categoría: {categoria_actual}"
            try:
                send_mail(
                    subject=asunto,
                    message=cuerpo_mensaje,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['annavillegas@live.com.ar'],
                    fail_silently=False,
                )
                messages.success(request, "¡Tu solicitud fue enviada con éxito!")
            except Exception as e:
                print(f"Error al enviar mail al administrador: {e}")
                messages.success(request, "¡Tu solicitud fue recibida correctamente!")

            return redirect('contacto')
    else:
        form = ContactoForm()
    return render(request, 'mi_app/contacto.html', {'form': form})

def eventos(request):
    return render(request, 'mi_app/eventos.html')


# --- Vistas de Autenticación ---

def registro_view(request):
    paso = request.session.get('registro_paso', 1)

    if request.method == 'POST':
        if paso == 1:
            form_paso1 = RegistroDatosBasicosForm(request.POST)
            if form_paso1.is_valid():
                email_ingresado = form_paso1.cleaned_data.get('email')

                try:
                    usuario_autorizado = UsuarioPermitido.objects.get(email=email_ingresado)

                    request.session['datos_registro'] = request.POST.copy()
                    request.session['registro_paso'] = 2

                    enlace_validacion = request.build_absolute_uri(reverse('registro'))
                    asunto = "Validación de cuenta — Eclipse Night Club"
                    mensaje = (
                        f"Hola {usuario_autorizado.nombre},\n\n"
                        f"Para completar tu registro, ingresá al siguiente enlace:\n{enlace_validacion}\n\n"
                        f"Tu código de validación es: {usuario_autorizado.codigo_validation}\n\n"
                        f"Saludos,\nEquipo de Sistemas Eclipse."
                    )

                    send_mail(
                        asunto,
                        mensaje,
                        settings.DEFAULT_FROM_EMAIL,
                        [email_ingresado],
                        fail_silently=False,
                    )

                    messages.info(request, "Le llegará un correo para validar su cuenta.")

                    form_paso2 = ValidacionCodigoForm()
                    return render(request, 'registration/registro.html', {'form': form_paso2, 'paso': 2})

                except UsuarioPermitido.DoesNotExist:
                    messages.error(request, "Acceso restringido. No está autorizado a utilizar este sistema.")
                    return render(request, 'registration/registro.html', {'form': form_paso1, 'paso': 1})

            return render(request, 'registration/registro.html', {'form': form_paso1, 'paso': 1})

        elif paso == 2:
            form_paso2 = ValidacionCodigoForm(request.POST)
            if form_paso2.is_valid():
                codigo = form_paso2.cleaned_data['codigo_acceso']
                datos_iniciales = request.session.get('datos_registro')

                if datos_iniciales:
                    email = datos_iniciales.get('email')
                    permitido = UsuarioPermitido.objects.filter(email=email, codigo_validation=codigo).exists()

                    if permitido:
                        form_final = RegistroDatosBasicosForm(datos_iniciales)
                        if form_final.is_valid():
                            user = form_final.save(commit=False)
                            user.username = datos_iniciales.get('username')
                            user.first_name = datos_iniciales.get('first_name')
                            user.last_name = datos_iniciales.get('last_name')
                            user.email = email
                            user.set_password(datos_iniciales.get('password1'))

                            user.is_staff = True
                            user.is_superuser = True
                            user.save()

                            request.session.pop('datos_registro', None)
                            request.session.pop('registro_paso', None)

                            messages.success(request, "Cuenta habilitada con éxito. Ya podés iniciar sesión.")
                            return redirect('login')
                    else:
                        form_paso2.add_error('codigo_acceso', "El código ingresado es incorrecto.")

            return render(request, 'registration/registro.html', {'form': form_paso2, 'paso': 2})

    else:
        request.session['registro_paso'] = 1
        form = RegistroDatosBasicosForm()
        return render(request, 'registration/registro.html', {'form': form, 'paso': 1})

def login_personalizado_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def home_view(request):
    return render(request, 'mi_app/home.html')


class PersonalisedPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            messages.error(
                self.request,
                "El correo electrónico ingresado no se encuentra registrado en nuestro sistema."
            )
            return self.form_invalid(form)

        messages.success(self.request, "Te hemos enviado un correo con las instrucciones.")
        return super().form_valid(form)

# --- Panel de Administración del Cliente ---

@login_required
def dashboard_admin(request):
    solicitudes = SolicitudConsulta.objects.all().order_by('-fecha_creacion')

    totales = {
        'total': solicitudes.count(),
        'comercial': solicitudes.filter(categoria_asignada='Consulta Comercial').count(),
        'tecnica': solicitudes.filter(categoria_asignada='Consulta Técnica').count(),
        'rrhh': solicitudes.filter(categoria_asignada='Consulta de RRHH').count(),
        'general': solicitudes.filter(categoria_asignada='Consulta General').count(),
    }

    return render(request, 'admin/dashboard.html', {
        'solicitudes': solicitudes,
        'totales': totales
    })

@login_required
def editar_consulta(request, pk):
    consulta = get_object_or_404(SolicitudConsulta, pk=pk)
    if request.method == 'POST':
        form = ContactoForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            messages.success(request, "Consulta actualizada correctamente.")
            return redirect('dashboard')
    else:
        form = ContactoForm(instance=consulta)

    return render(request, 'admin/editar_consulta.html', {'form': form, 'consulta': consulta})

@login_required
def eliminar_consulta(request, pk):
    consulta = get_object_or_404(SolicitudConsulta, pk=pk)
    if request.method == 'POST':
        consulta.delete()
        messages.success(request, "Consulta eliminada exitosamente.")
        return redirect('dashboard')

    return render(request, 'admin/eliminar_consulta_confirm.html', {'consulta': consulta})

@login_required
def cms_admin(request):
    contenido, _ = ContenidoInicio.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ContenidoInicioForm(request.POST, instance=contenido)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Contenido de la web actualizado con éxito!")
            return redirect('cms_admin')
    else:
        form = ContenidoInicioForm(instance=contenido)

    return render(request, 'admin/cms_dashboard.html', {
        'form': form,
        'contenido': contenido
    })


# --- APIs (Interna y Externa consumida mediante DRF) ---

class ConsultasAPIView(APIView):
    """API Interna para consultar las solicitudes en formato JSON."""
    def get(self, request):
        consultas = SolicitudConsulta.objects.all().order_by('-fecha_creacion')
        serializer = SolicitudConsultaSerializer(consultas, many=True)
        return Response(serializer.data)

class EventosExternosAPIView(APIView):
    def get(self, request):
        url_eventos = "https://api.tvmaze.com/search/shows?q=festival"
        try:
            response = requests.get(url_eventos, timeout=5)
            if response.status_code == 200:
                data = response.json()[:6]
                return Response(data, status=status.HTTP_200_OK)
            return Response({'error': 'No se obtuvieron datos de la API externa'}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)