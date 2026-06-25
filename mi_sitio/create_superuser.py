from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

try:
    User = get_user_model()

    if not User.objects.filter(username="postgres").exists():
        User.objects.create_superuser(username="postgres", email="", password="Django")
        print("Created superuser")

    else:
        print("Superuser already exists")

except OperationalError:
    print("La base de datos aún no esta lista. Intentá de nuevo tras migraciones.")