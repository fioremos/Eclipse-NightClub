from django.contrib import admin
from .models import SolicitudConsulta, RegistroReserva, RegistroConsulta, RegistroEvento, UsuarioPermitido


class BaseSolicitudAdmin(admin.ModelAdmin):
    change_list_template = "admin/admin_change_list.html"
    list_display = ('id', 'nombre_completo', 'correo_electronico', 'categoria_asignada', 'fecha_reserva',
                    'fecha_creacion')
    list_editable = ('categoria_asignada',)
    list_filter = ('categoria_asignada', 'fecha_creacion')
    search_fields = ('nombre_completo', 'correo_electronico', 'mensaje')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context['totales'] = {
            'total': SolicitudConsulta.objects.count(),
            'comercial': SolicitudConsulta.objects.filter(categoria_asignada='Comercial').count(),
            'tecnica': SolicitudConsulta.objects.filter(categoria_asignada='Tecnica').count(),
            'rrhh': SolicitudConsulta.objects.filter(categoria_asignada='RRHH').count(),
            'general': SolicitudConsulta.objects.filter(categoria_asignada='General').count(),
        }

        return super().changelist_view(request, extra_context=extra_context)

@admin.register(RegistroReserva)
class RegistroReservaAdmin(BaseSolicitudAdmin):
    list_display = BaseSolicitudAdmin.list_display + ('cantidad_personas',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo_consulta_cliente='mesa')


@admin.register(RegistroConsulta)
class RegistroConsultaAdmin(BaseSolicitudAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo_consulta_cliente='general')


@admin.register(RegistroEvento)
class RegistroEventoAdmin(BaseSolicitudAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo_consulta_cliente='evento')


@admin.register(UsuarioPermitido)
class UsuarioPermitidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'codigo_validation')
    search_fields = ('nombre', 'email', 'codigo_validation')
    ordering = ('nombre',)

admin.site.site_header = "Eclipse Night Club — Panel de Control"
admin.site.site_title = "Eclipse Admin"
admin.site.index_title = "Gestión del Sistema y Solicitudes"