from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    name = 'analytics'
    # TODO: Uncomment this to start using "analytics" db across the app
    _DATABASE = 'analytics'
