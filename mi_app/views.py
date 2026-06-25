from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from django.conf import settings
from .forms import ContactoForm, RegistroDatosBasicosForm, ValidacionCodigoForm
from .models import SolicitudConsulta, UsuarioPermitido
from .serializers import SolicitudConsultaSerializer


# Create your views here.
def inicio(request):
    return render(request, 'mi_app/inicio.html')

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
            nueva_solicitud = SolicitudConsulta(
                nombre_completo=form.cleaned_data.get('nombre_completo'),
                correo_electronico=form.cleaned_data.get('correo_electronico'),
                tipo_consulta_cliente=form.cleaned_data.get('tipo_consulta_cliente'),
                mensaje=form.cleaned_data.get('mensaje'),
                fecha_reserva=form.cleaned_data.get('fecha_reserva'),
                cantidad_personas=form.cleaned_data.get('cantidad_personas')
            )
            form.save()
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
    data = [
        {
            'dia': '22', 'mes': 'FEB', 'nombre': 'TECHNO NIGHT: ALVEZ',
            'genero': 'Techno / Dark Progressive',
            'imagen': 'imagenes/dj1.png',
            'descripcion': 'Una noche inmersiva con los ritmos más potentes del underground.'
        },
        {
            'dia': '01', 'mes': 'MAR', 'nombre': 'NEON VIBES',
            'genero': 'EDM / House',
            'imagen': 'imagenes/dj2.png',
            'descripcion': 'El evento temático más esperado con decoración flúor y shows láser.'
        },
    ]
    return render(request, 'mi_app/eventos.html', {'lista_eventos': data})

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
                        'no-reply@eclipsenightclub.com',
                        [email_ingresado],
                        fail_silently=False,
                    )

                    messages.info(request, "Le llegará un correo para validar su cuenta.")
                    return redirect('registro')

                except UsuarioPermitido.DoesNotExist:
                    messages.error(request, "Acceso restringido. No está autorizado a utilizar este sistema.")
                    return redirect('registro')

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
                            user.username = email
                            user.first_name = datos_iniciales.get('first_name')
                            user.last_name = datos_iniciales.get('last_name')
                            user.email = email
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


def lista_eventos_api_view(request):

    url_eventos = "https://api.tvmaze.com/search/shows?q=festival"
    eventos_api = []
    response = requests.get(url_eventos, timeout=5)
    if response.status_code == 200:
        eventos_api = response.json()[:6]

    return render(request, 'mi_app/eventos.html', {'eventos': eventos_api})

def login_personalizado_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def home_view(request):
    return render(request, 'mi_app/home.html')

class ConsultasAPIView(APIView):
    def get(self, request):
        consultas = SolicitudConsulta.objects.all().order_by('-fecha_creacion')
        serializer = SolicitudConsultaSerializer(consultas, many=True)
        return Response(serializer.data)