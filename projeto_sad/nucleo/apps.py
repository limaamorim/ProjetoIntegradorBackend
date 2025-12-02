from django.apps import AppConfig


class NucleoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nucleo'

class SimuladorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'simulador'