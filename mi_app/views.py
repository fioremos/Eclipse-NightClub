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
from pathlib import Path

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from .forms import ContactoForm, RegistroDatosBasicosForm, ValidacionCodigoForm, ContenidoInicioForm
from .models import SolicitudConsulta, UsuarioPermitido, ContenidoInicio
from .serializers import SolicitudConsultaSerializer


def _get_email_css():
    css_path = Path(__file__).resolve().parent.parent / 'static' / 'css' / 'email_styles.css'
    try:
        return css_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


def _get_email_css_declarations(class_name):
    css = _get_email_css()
    match = re.search(rf"\.{re.escape(class_name)}\s*\{{([^}}]+)\}}", css, re.DOTALL)
    if not match:
        return ''
    declarations = [decl.strip() for decl in match.group(1).split(';') if decl.strip()]
    return '; '.join(declarations) + ';'


def _render_email_html(content):
    return f"""
    <div style="{_get_email_css_declarations('email-outer')}">
        <div style="{_get_email_css_declarations('email-wrapper')}">
            <div style="{_get_email_css_declarations('email-card')}">
                {content}
            </div>
        </div>
    </div>
    """


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
            nombre = form.cleaned_data.get('nombre_completo')
            correo_cliente = form.cleaned_data.get('correo_electronico')
            fecha_reserva = form.cleaned_data.get('fecha_reserva') or 'No aplica'
            cantidad_personas = form.cleaned_data.get('cantidad_personas') or 'No aplica'
            mensaje_usuario = form.cleaned_data.get('mensaje')

            cuerpo_texto_plano = f"""
                        Nueva Solicitud en Eclipse NightClub
                        ------------------------------------
                        Categoría: {categoria_actual}
                        Nombre: {nombre}
                        Correo: {correo_cliente}
                        Fecha Solicitada: {fecha_reserva}
                        Cantidad de Personas: {cantidad_personas}
                        Mensaje: {mensaje_usuario}
                        """

            cuerpo_html = _render_email_html(f"""
                        <div style="{_get_email_css_declarations('email-header')}">
                            <h1 style="{_get_email_css_declarations('email-title')}">ECLIPSE</h1>
                            <h3 style="{_get_email_css_declarations('email-subtitle')}">NIGHT CLUB</h3>
                        </div>
                        <hr style="{_get_email_css_declarations('email-divider')}">

                        <h3 style="{_get_email_css_declarations('email-section-title')}">Nueva Solicitud Registrada</h3>

                        <div style="{_get_email_css_declarations('email-info-box')}">
                            <p style="{_get_email_css_declarations('email-text')}"><span style="{_get_email_css_declarations('email-label')}">Categoría:</span> {categoria_actual}</p>
                            <p style="{_get_email_css_declarations('email-text')}"><span style="{_get_email_css_declarations('email-label')}">Nombre:</span> {nombre}</p>
                            <p style="{_get_email_css_declarations('email-text')}"><span style="{_get_email_css_declarations('email-label')}">Email:</span> {correo_cliente}</p>
                            <p style="{_get_email_css_declarations('email-text')}"><span style="{_get_email_css_declarations('email-label')}">Fecha Reserva:</span> {fecha_reserva}</p>
                            <p style="{_get_email_css_declarations('email-text')}"><span style="{_get_email_css_declarations('email-label')}">Personas:</span> {cantidad_personas}</p>
                            <hr style="border-color: #2a2a35; margin: 15px 0;">
                            <p style="{_get_email_css_declarations('email-message')}"><strong>Mensaje:</strong> "{mensaje_usuario}"</p>
                        </div>

                        <p style="{_get_email_css_declarations('email-footer')}">
                            Este registro fue almacenado correctamente en PostgreSQL.
                        </p>
                        """)

            asunto = f"Nueva Solicitud — Categoría: {categoria_actual}"

            mensaje_mail = EmailMultiAlternatives(
                subject=asunto,
                body=cuerpo_texto_plano,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@eclipse.com'),
                to=['annavillegas@live.com.ar']
            )
            mensaje_mail.attach_alternative(cuerpo_html, "text/html")

            try:
                mensaje_mail.send()
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
                    cuerpo_texto_plano = (
                        f"Hola {usuario_autorizado.nombre},\n\n"
                        f"Para completar tu registro, ingresá al siguiente enlace:\n{enlace_validacion}\n\n"
                        f"Tu código de validación es: {usuario_autorizado.codigo_validation}\n\n"
                        f"Saludos,\nEquipo de Sistemas Eclipse."
                    )

                    cuerpo_html = _render_email_html(f"""
                                        <div style="{_get_email_css_declarations('email-header')}">
                                            <h1 style="{_get_email_css_declarations('email-title')}">ECLIPSE</h1>
                                            <h3 style="{_get_email_css_declarations('email-subtitle')}">NIGHT CLUB</h3>
                                        </div>
                                        <hr style="{_get_email_css_declarations('email-divider')}">

                                        <p style="{_get_email_css_declarations('email-text')}; font-size: 16px;">Hola <strong style="{_get_email_css_declarations('email-label')}">{usuario_autorizado.nombre}</strong>,</p>
                                        <p style="{_get_email_css_declarations('email-muted')}">Para completar el proceso de registro en el sistema administrativo de Eclipse Night Club, ingresá tu código de validación en la plataforma:</p>

                                        <div style="{_get_email_css_declarations('email-code-box')}">
                                            <span style="{_get_email_css_declarations('email-code-label')}">Tu Código de Validación</span>
                                            <span style="{_get_email_css_declarations('email-code')}">{usuario_autorizado.codigo_validation}</span>
                                        </div>

                                        <div style="{_get_email_css_declarations('email-button-row')}">
                                            <a href="{enlace_validacion}" style="{_get_email_css_declarations('email-button')}; {_get_email_css_declarations('email-button-pink')}">IR A LA PLATAFORMA</a>
                                        </div>

                                        <p style="{_get_email_css_declarations('email-footer')}">
                                            Equipo de Sistemas — Eclipse Night Club
                                        </p>
                                        """)

                    mensaje_mail = EmailMultiAlternatives(
                        subject=asunto,
                        body=cuerpo_texto_plano,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eclipse.com'),
                        to=[email_ingresado]
                    )
                    mensaje_mail.attach_alternative(cuerpo_html, "text/html")

                    try:
                        mensaje_mail.send()
                    except Exception as e:
                        print("Error al enviar mail de validación:", e)

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


def olvide_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        users = User.objects.filter(email=email)

        if users.exists():
            user = users.first()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            link_recuperacion = request.build_absolute_uri(
                reverse('restablecer_password', kwargs={'uidb64': uid, 'token': token})
            )

            cuerpo_html = _render_email_html(f"""
                        <div style="{_get_email_css_declarations('email-header')}">
                            <h1 style="{_get_email_css_declarations('email-title')}">ECLIPSE</h1>
                            <h3 style="{_get_email_css_declarations('email-subtitle')}">NIGHT CLUB</h3>
                        </div>
                        <hr style="{_get_email_css_declarations('email-divider')}">
                        <p style="{_get_email_css_declarations('email-text')}; font-size: 16px; margin-bottom: 10px;">
                            Hola <strong style="{_get_email_css_declarations('email-label')}; display: inline;">{user.first_name or user.username}</strong>,
                        </p>
                        <p style="{_get_email_css_declarations('email-muted')}">Recibimos una solicitud para restablecer la contraseña de tu cuenta en Eclipse NightClub.</p>
                        <div style="{_get_email_css_declarations('email-button-row')}">
                            <a href="{link_recuperacion}" style="{_get_email_css_declarations('email-button')}; {_get_email_css_declarations('email-button-pink')}">RESTABLECER CONTRASEÑA</a>
                        </div>
                        <p style="{_get_email_css_declarations('email-footer')}">Si no solicitaste este cambio, podés ignorar este correo de forma segura.</p>
                        """)

            mensaje_mail = EmailMultiAlternatives(
                subject="Restablecer Contraseña — Eclipse Night Club",
                body=f"Para restablecer tu contraseña ingresá a: {link_recuperacion}",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eclipse.com'),
                to=[email]
            )
            mensaje_mail.attach_alternative(cuerpo_html, "text/html")

            try:
                mensaje_mail.send()
            except Exception as e:
                print("Error enviando mail:", e)

            messages.success(request, "Te hemos enviado un correo con las instrucciones para restablecer tu clave.")
            return redirect('login')
        else:
            messages.error(request, "El correo ingresado no corresponde a ningún usuario registrado.")
            return render(request, 'registration/olvide_password.html')

    return render(request, 'registration/olvide_password.html')

def restablecer_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            pass1 = request.POST.get('password1')
            pass2 = request.POST.get('password2')

            if pass1 and pass1 == pass2:
                user.set_password(pass1)
                user.save()
                messages.success(request, "¡Contraseña restablecida con éxito! Ya podés iniciar sesión.")
                return redirect('login')
            else:
                messages.error(request, "Las contraseñas no coinciden o están vacías.")

        return render(request, 'registration/nueva_password.html', {'validlink': True})
    else:
        messages.error(request, "El enlace de recuperación es inválido o ha expirado.")
        return render(request, 'registration/nueva_password.html', {'validlink': False})

# --- Panel de Administración del Cliente ---

@login_required
def dashboard_admin(request):
    solicitudes = SolicitudConsulta.objects.all().order_by('-fecha_creacion')

    totales = {
        'total': solicitudes.count(),
        'comercial': solicitudes.filter(categoria_asignada='Comercial').count(),
        'tecnica': solicitudes.filter(categoria_asignada='Tecnica').count(),
        'rrhh': solicitudes.filter(categoria_asignada='RRHH').count(),
        'general': solicitudes.filter(categoria_asignada='General').count(),
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