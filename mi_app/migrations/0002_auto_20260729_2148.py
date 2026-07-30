from django.db import migrations


def cargar_usuarios_permitidos(apps, schema_editor):
    # Obtenemos el modelo desde el histórico de la migración
    UsuarioPermitido = apps.get_model('mi_app', 'UsuarioPermitido')  # Cambiá 'mi_app' por tu app

    UsuarioPermitido.objects.get_or_create(
        email="annavillegas@live.com.ar",
        defaults={
            "nombre": "Analía Villegas",
            "codigo_validation": "ECLIPSE2026"
        }
    )

    UsuarioPermitido.objects.get_or_create(
        email="fimosca97@gmail.com",
        defaults={
            "nombre": "Fiorella",
            "codigo_validation": "123456789"
        }
    )


class Migration(migrations.Migration):
    dependencies = [
        ('mi_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(cargar_usuarios_permitidos),
    ]