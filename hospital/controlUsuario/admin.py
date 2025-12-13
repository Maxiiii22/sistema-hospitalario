from django.contrib import admin
from .models import Persona,Usuario,TiposUsuarios,RolesProfesionales
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# Register your models here.


# Creamos un admin personalizado ya que como elimine username y ahora uso login_id, el UserAdmin por defecto de Django no sabe cómo manejar el modelo correctamente, entonces: El admin no usa el formulario correcto para cambiar la contraseña, el campo password se ve como texto plano,La contraseña se guarda como texto plano.
# La solución entonces es usar un PersonaAdmin personalizado:  Tenés que crear una clase PersonaAdmin basada en UserAdmin, y decirle a Django cómo manejar tu modelo personalizado.
class PersonaAdmin(BaseUserAdmin):
    model = Persona
    list_display = ('login_id', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'sexo')
    ordering = ('login_id',)
    search_fields = ('login_id', 'first_name', 'last_name', 'dni')

    # Reemplazamos el campo username por login_id en los fieldsets
    fieldsets = (
        (None, {'fields': ('login_id', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'dni', 'fecha_nacimiento', 'sexo', 'telefono')}),
        (_('Permisos'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login_id', 'first_name', 'last_name', 'dni', 'fecha_nacimiento', 'sexo', 'telefono', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )



# Admin personalizado para el modelo Usuario
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'persona', 'numero_matricula',"debe_cambiar_contraseña", 'tipoUsuario']

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Llama a clean(), lo que valida unicidad condicional, etc.
        super().save_model(request, obj, form, change)

# Admin personalizado para el modelo tiposUsuario
class TiposUsuariosAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_tipoUsuario']

# Admin personalizado para el modelo Roles Profesionales
class RolesProfesionalesAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_rol_profesional', 'tipoUsuario','especialidad','servicio_diagnostico']

admin.site.register(Persona,PersonaAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(TiposUsuarios,TiposUsuariosAdmin)
admin.site.register(RolesProfesionales,RolesProfesionalesAdmin)


