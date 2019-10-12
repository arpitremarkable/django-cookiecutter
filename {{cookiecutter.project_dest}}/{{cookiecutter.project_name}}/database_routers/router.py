from django.apps import apps
from django.conf import settings


DB_APP_ROUTER = getattr(settings, 'DB_APP_ROUTER', {})
"""
example:
    DB_APP_ROUTER = {
        'analytics': (
            'analytics',
            'ga_app',
        ),
        'pii': (
            'data_store',
        ),
    }
"""

DB_MODEL_ROUTER = getattr(settings, 'DB_MODEL_ROUTER', {})
"""
example:
    DB_MODEL_ROUTER = {
        'pii': (
            'travel_insurance_plan.TripDetailFormStore',  # Model._meta.label
            'travel_insurance_proposal.ProposalFormStore',
        ),
    }
"""


_ROUTER_CACHE = {}


class Router(object):

    @classmethod
    def _get_db_name_from_settings(cls, setting_dict, value):
        for db_name, values in setting_dict.items():
            if value in values:
                return db_name

    def _get_db_for_app(self, app_label):
        return (
            self._get_db_name_from_settings(setting_dict=DB_APP_ROUTER, value=app_label) or
            getattr(apps.app_configs[app_label], "_DATABASE", None)
        )

    def _get_db_for_model(self, model):
        if model not in _ROUTER_CACHE:
            db = self._get_db_name_from_settings(setting_dict=DB_MODEL_ROUTER, value=model._meta.label)
            if db is None:
                db = self._get_db_name_from_settings(setting_dict=DB_APP_ROUTER, value=model._meta.app_label)
            if db is None:
                db = getattr(model, "_DATABASE", None)
            if db is None:
                db = getattr(apps.app_configs[model._meta.app_label], "_DATABASE", None)

            # If custom database doesn't exist then let it go inside default db
            if db is not None and not self.db_exists(db) and settings.ALLOW_DATABASE_UNION:
                db = None

            _ROUTER_CACHE[model] = db
        return _ROUTER_CACHE[model]

    def db_exists(self, db_name):
        db_exists = db_name in settings.DATABASES
        if db_name and not settings.ALLOW_DATABASE_UNION:
            assert db_exists, f"Database {db_name} doesn't exist, but it's referenced in DB ROUTER settings"
        return db_exists

    def db_for_read(self, model, **hints):
        db = self._get_db_for_model(model)
        if self.db_exists(db):
            return db
        return

    def db_for_write(self, model, **hints):
        db = self._get_db_for_model(model)
        if self.db_exists(db):
            return db
        return

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if 'target_db' in hints:
            return db == hints['target_db']
        try:
            model = apps.get_model(app_label, model_name)
        except ValueError:
            if not model_name:
                # For datamigration operations
                app_db = self._get_db_for_app(app_label)
                app_db = app_db or 'default'
                if db == app_db:
                    return True
                else:
                    return False
            else:
                return None
        else:
            if self.db_exists(db):
                model_db = self._get_db_for_model(model)
                model_db = model_db or 'default'
                if db == model_db:
                    return True
                else:
                    return False
            else:
                return None
