from django.contrib import admin
from .models import MakeModel, MakeField, MakeMigration


class MakeFieldInline(admin.TabularInline):
    model = MakeField


class MakeModelAdmin(admin.ModelAdmin):
    inlines = [MakeFieldInline]


class MakeMigrationAdmin(admin.ModelAdmin):
    pass


admin.site.register(MakeMigration, MakeMigrationAdmin)
admin.site.register(MakeModel, MakeModelAdmin)
