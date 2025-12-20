# Sistema Hospitalario

Sistema Hospitalario desarrollado en Django con MySQL, HTML, CSS y JavaScript, pensado para gestionar pacientes, personal y turnos de manera eficiente.

![Vista previa](imagenes%20previas/hospital-1.jpg)

## Funcionalidades principales

### Módulo del Paciente
- Visualizar historial clínico: consultas, estudios y resultados.
- Solicitar turnos para citas médicas o estudios con orden médica.
- Registrar y gestionar menores a cargo, incluyendo turnos y historial.
  
![Vista previa](imagenes%20previas/hospital-2.jpg)

### Módulo del Personal
#### Superadmin:
Este es el rol más alto en términos de permisos. El administrador tiene acceso a la gestión completa del sistema, administración de usuarios y configuración general.
- **Gestión de usuarios:**
  - Activar y desactivar usuarios del personal.
  - Editar información del personal.
  - Restablecer contraseñas.
  - Asignar y desasignar roles y lugares de trabajo.
- **Gestión de datos base del sistema:**
  - Especialidades médicas.
  - Servicios de diagnóstico.
  - Estudios.
  - Lugares del hospital (habitaciones, consultorios, oficinas).
  - Departamentos.
  - Identidades y roles.

![Vista previa](imagenes%20previas/hospital-3.jpg)


## Notas
- Incluye archivo SQL con datos iniciales en `Documentacion/`.  
- Ejecutar migraciones antes de iniciar el servidor para configurar la base de datos local.

