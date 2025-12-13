from django.contrib import admin
from .models import Paciente,MenorACargoDePaciente

# Register your models here.

class MenorACargoDePacienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'adulto','menor','parentesco']


admin.site.register(Paciente)
admin.site.register(MenorACargoDePaciente,MenorACargoDePacienteAdmin)