from django.apps import AppConfig


class MetaConfig(AppConfig):
    name = 'meta'

    def ready(self):
        import meta.signals
        meta.signals.reload_models()
        meta.signals.reload_urls()
