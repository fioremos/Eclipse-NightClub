from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import SolicitudConsulta
from datetime import date

class ContactoForm(forms.ModelForm):
    class Meta:
        model = SolicitudConsulta
        fields = ['nombre_completo', 'correo_electronico', 'tipo_consulta_cliente', 'fecha_reserva',
                  'cantidad_personas', 'mensaje']

        widgets = {
            'nombre_completo': forms.TextInput(attrs={'id': 'nombre', 'required': True}),
            'correo_electronico': forms.EmailInput(attrs={'id': 'email', 'required': True}),
            'tipo_consulta_cliente': forms.Select(attrs={'id': 'tipo'}, choices=[
                ('mesa', 'Reserva de Mesa'),
                ('evento', 'Evento Privado'),
                ('general', 'Consulta General'),
            ]),
            'fecha_reserva': forms.DateInput(attrs={'id': 'fecha', 'type': 'date'}),
            'cantidad_personas': forms.NumberInput(attrs={'id': 'personas', 'min': '1'}),
            'mensaje': forms.Textarea(attrs={'id': 'mensaje', 'rows': 6}),
        }

        def clean_nombre_completo(self):
            nombre = self.cleaned_data.get('nombre_completo', '').strip()
            if len(nombre) < 4:
                raise forms.ValidationError("El nombre completo debe tener al menos 4 caracteres.")
            return nombre

        def clean_fecha_reserva(self):
            fecha = self.cleaned_data.get('fecha_reserva')
            tipo = self.cleaned_data.get('tipo_consulta_cliente')

            if tipo in ['mesa', 'evento'] and not fecha:
                raise forms.ValidationError("Para reservas de mesas o eventos debes seleccionar una fecha.")

            if fecha and fecha < date.today():
                raise forms.ValidationError("La fecha de reserva no puede ser una fecha pasada.")
            return fecha

        def clean_cantidad_personas(self):
            personas = self.cleaned_data.get('cantidad_personas')
            tipo = self.cleaned_data.get('tipo_consulta_cliente')

            if tipo in ['mesa', 'evento']:
                if not personas:
                    raise forms.ValidationError("Debes indicar la cantidad de personas para la reserva.")
                if personas < 1:
                    raise forms.ValidationError("La cantidad de personas debe ser al menos 1.")
            return personas

        def clean_mensaje(self):
            mensaje = self.cleaned_data.get('mensaje', '').strip()
            if len(mensaje) < 10:
                raise forms.ValidationError("El mensaje es demasiado corto (mínimo 10 caracteres).")
            return mensaje

class RegistroDatosBasicosForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label="Nombre", required=True)
    last_name = forms.CharField(max_length=30, label="Apellido", required=True)
    email = forms.EmailField(label="Correo Electrónico", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

class ValidacionCodigoForm(forms.Form):
    codigo_acceso = forms.CharField(
        max_length=50,
        label="Código de Validación Empresarial",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Ingresá el código provisto por la empresa'})
    )