from django.contrib.auth import get_user_model
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


def create_superuser_if_needed():
    try:
        if not connection.introspection.table_names():
            return

        if "auth_user" not in connection.introspection.table_names():
            return

        User = get_user_model()
        if not User.objects.filter(username="postgres").exists():
            User.objects.create_superuser(username="postgres", email="", password="Django")
            print("Created superuser")
        else:
            print("Superuser already exists")
    except (OperationalError, ProgrammingError):
        print("La base de datos aún no está lista. Intentá de nuevo tras migraciones.")


create_superuser_if_needed()