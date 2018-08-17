import importlib
import types

from django.apps import apps
from django.conf import settings
from django.db import connection, models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from django.urls.base import clear_url_caches


from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.questioner import (
    MigrationQuestioner
)
from django.db.migrations.state import ProjectState
from django.db.migrations.writer import MigrationWriter

from .models import MakeModel, MakeField, MakeMigration


def reload_models():
    for makemodel in MakeModel.objects.all():
        attrs = {'__module__': 'meta'}
        for field in makemodel.makefield_set.all():
            model_field_cls = getattr(models, field.field_type)
            attrs[field.name] = model_field_cls()
        model_cls = type(
            makemodel.name,
            (models.Model, ),
            attrs,
        )

        reload_admin(model_cls)


def reload_admin(model_cls):
    found_model = False
    for registered_model in admin.site._registry.copy():
        if registered_model.__name__ == model_cls.__name__:
            found_model = registered_model
    if found_model:
        admin.site.unregister(found_model)
        admin.site.register(model_cls)
    else:
        admin.site.register(model_cls)


class NonInteractiveMigrationQuestioner(MigrationQuestioner):

    def ask_not_null_addition(self, field_name, model_name):
        field = apps.get_model(
            'meta', model_name)._meta.get_field(field_name)
        if isinstance(field, models.TextField):
            return ''
        if isinstance(field, models.IntegerField):
            return 0

    def ask_not_null_alteration(self, field_name, model_name):
        # We can't ask the user, so set as not provided.
        return ''


def write_migration_rows(changes):
    for app_label, app_migrations in changes.items():
        for migration in app_migrations:
            writer = MigrationWriter(migration)
            migration_string = writer.as_string()
            MakeMigration.objects.create(
                name=writer.migration.name,
                content=migration_string
            )


class MyLoader(importlib.machinery.SourceFileLoader):
    def get_data(self, path):
        return MakeMigration.objects.get(name=path).content


def existing_migrations():
    existing = {}
    for makemigration in MakeMigration.objects.all():
        loader = MyLoader('a_b', makemigration.name)
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)
        existing[('meta', makemigration.name)] = mod.Migration(
            makemigration.name, 'meta')
    return existing


def write_migrations():
    import django.db.migrations.loader
    old_load_disk = django.db.migrations.loader.MigrationLoader.load_disk

    def load_disk(self):
        old_load_disk(self)
        self.disk_migrations.update(existing_migrations())

    django.db.migrations.loader.MigrationLoader.load_disk = load_disk

    loader = MigrationLoader(None, ignore_no_migrations=True)
    questioner = NonInteractiveMigrationQuestioner()
    autodetector = MigrationAutodetector(
        loader.project_state(),
        ProjectState.from_apps(apps),
        questioner,
    )
    app_label = 'meta'
    app_labels = {app_label, }
    changes = autodetector.changes(
        graph=loader.graph,
        trim_to_apps=app_labels,
        convert_apps=app_labels,
        migration_name=None,
    )
    write_migration_rows(changes)


def migration_progress_callback(action, migration=None, fake=False):
    print("action", action)
    print("migration", migration)


def migrate_migrations():
    app_label = 'meta'
    executor = MigrationExecutor(connection, migration_progress_callback)
    pre_migrate_state = executor._create_project_state(
        with_applied_migrations=True)

    targets = [key for key in executor.loader.graph.leaf_nodes(app_label)
               if key[0] == app_label]
    plan = executor.migration_plan(targets)
    if plan:
        post_migrate_state = executor.migrate(
            targets, plan=plan, state=pre_migrate_state.clone(), fake=False,
            fake_initial=False,
        )


def reload_urls():
    importlib.reload(importlib.import_module(settings.ROOT_URLCONF))
    clear_url_caches()


@receiver(post_save, sender=MakeModel)
def model_save(sender, instance, created, **kwargs):
    reload_models()
    write_migrations()
    migrate_migrations()
    apps.clear_cache()
    reload_urls()


@receiver(post_save, sender=MakeField)
def field_save(sender, instance, created, **kwargs):
    reload_models()
    write_migrations()
    migrate_migrations()
    apps.clear_cache()
    reload_urls()
