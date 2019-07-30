from django.apps import AppConfig


class MainAppConfig(AppConfig):
    name = "mlm.apps.main"
    label = "main"
    verbose_name = "Main App"

    def ready(self):
        import mlm.apps.main.signals


# This is how we register our custom app config with Django. Django is smart
# enough to look for the 'default_app_config' property of each registered app
# and use the correct app config based on that value.
default_app_config = "mlm.apps.main.MainAppConfig"
