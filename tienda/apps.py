from django.apps import AppConfig

class TiendaConfig(AppConfig):
    name = 'tienda'

    def ready(self):
        import tienda.signals
