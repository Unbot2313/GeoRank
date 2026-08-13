from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    name = 'analysis'

    def ready(self):
        from . import signals  # noqa: F401