from django.apps import AppConfig
import sys

class GestionUsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_usuarios'

    def ready(self):
        if 'runserver' in sys.argv:
            from .scheduler import start_scheduler
            start_scheduler()
