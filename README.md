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
#### Superadministrador:
Este es el rol más alto en términos de permisos. El Superadministrador tiene acceso a la gestión completa del sistema, administración de usuarios y configuración general.
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

### Administrador
Segundo rol con mayor nivel de permisos dentro del sistema. Responsable de la gestión operativa del personal no crítico y del seguimiento de la actividad clínica.
- **Gestión de usuarios no críticos (enfermería y médicos):**
  - Editar información del personal.
  - Restablecer contraseñas.
- **Gestión de agendas médicas:**
  - Administrar agendas de médicos.
  - Reprogramar o cancelar citas en casos donde el médico o el paciente no puedan hacerlo.
- **Reportes y estadísticas:**
  - Visualizar reportes diarios y mensuales de consultas médicas.
  - Visualizar reportes diarios y mensuales de servicios de diagnóstico.
- **Productividad médica:**
  - Visualizar la productividad de los médicos por especialidad.
  - Consultar productividad diaria y mensual.
- **Gestión de cuentas de pacientes:**
  - Ver solicitudes de reactivación de cuentas de pacientes que fueron desactivadas de forma voluntaria tras dejar de utilizar los servicios del hospital.
  - Evaluar solicitudes de pacientes que desean recuperar su cuenta previamente activa.
  - Aprobar o rechazar solicitudes de reactivación.

![Vista previa](imagenes%20previas/hospital-4.jpg)

### Médico de consultorio
Rol encargado de la atención médica de los pacientes que solicitan turnos para consultas médicas.
- **Gestión de especialidades:**
  - Cambiar entre las especialidades que tenga asignadas.
- **Gestión de turnos:**
  - Visualizar sus turnos programados.
  - Reprogramar o cancelar turnos con la debida antelación.
- **Historial de atención:**
  - Consultar el historial de las consultas médicas realizadas.
  - Acceder a registros de citas médicas previamente atendidas.
- **Acceso a registros médicos:**
  - Acceder a los registros médicos de los pacientes que tienen turno asignado y que se encuentran bajo su atención.
- **Gestión de informes y diagnósticos:**
  - Crear, modificar y visualizar informes médicos.
  - Realizar diagnósticos.
  - Solicitar estudios médicos.
  - Prescribir medicamentos.

![Vista previa](imagenes%20previas/hospital-5.jpg)


## Notas
- Incluye archivo SQL con datos iniciales en `Documentacion/`.  
- Ejecutar migraciones antes de iniciar el servidor para configurar la base de datos local.

