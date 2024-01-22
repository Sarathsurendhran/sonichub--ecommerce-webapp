from django.apps import AppConfig

class OrderManagementMainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order_managements'

    def ready(self):
        import order_managements.models