# Sistema Hospitalario

Sistema Hospitalario desarrollado con Django y MySQL, con interfaz web en HTML, CSS y JavaScript.
Diseñado para centralizar y optimizar la gestión hospitalaria, permitiendo administrar turnos, consultas médicas, estudios, hospitalización y el historial clínico de los pacientes de manera eficiente.
El sistema interactúa con pacientes, personal hospitalario y administradores, ofreciendo un flujo de trabajo claro, seguro y fácil de usar.

![Vista previa](imagenes%20previas/hospital-1.jpg)


---

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

### Enfermero
Rol asociado a los profesionales de enfermería que brindan atención directa a los pacientes hospitalizados.
- **Atencion clinica de los pacientes a su cargo:**
- Registrar signos vitales.
- Documentar observaciones de evaluaciones diarias.
- Registrar procedimientos.
- Registrar medicacion administrada y horarios.
- **Acceso a información médica:**
- Consultar notas de enfermería previas de pacientes a su cargo.
- Visualizar indicaciones del médico hospitalario asignado.

![Vista previa](imagenes%20previas/hospital-6.jpg)

### Operador de resultados:
Este rol está asociado a las personas encargadas de subir y analizar los resultados de pruebas de laboratio,fisiologicos,imagenes y evaluaciones.
- **Gestión de resultados de estudios:**
- Analizar resultados de estudios y evaluaciones.
- Registrar y subir resultados al sistema para que estén disponibles para médicos y pacientes.

![Vista previa](imagenes%20previas/hospital-7.jpg)

### Jefe de enfermeria:
Este rol está asociado a las personas encargadas de supervisar los enfermeros y medicos hospitalarios de su unidad asignada.
- **Gestión de hospitalización:**
- Asignar habitaciones a pacientes hospitalizados.
- Asignar y desasignar médicos hospitalarios y enfermeros a pacientes.
- Supervisar evaluaciones médicas y notas de enfermería de los pacientes.
- **Supervisión de personal:**
- Consultar historial de evaluaciones de todos los médicos hospitalarios de la unidad.
- Consultar historial de notas de observación de todos los enfermeros de la unidad.


![Vista previa](imagenes%20previas/hospital-8.jpg)

### Medico Hospitalario:
Rol asociado a los médicos responsables de la evaluación, diagnóstico, tratamiento y seguimiento clínico de los pacientes hospitalizados. Este rol tiene acceso ampliado a información clínica y herramientas de decisión médica.
- **Atención integral de pacientes asignados:**
- Evaluar y registrar la evolución clínica de los pacientes.
- Registrar diagnósticos y prescribir medicación u órdenes médicas.
- Acceder a todas las notas de observación de los enfermeros asignados a sus pacientes.
- **Supervisión y coordinación:**
- Supervisar enfermeros a cargo de mis pacientes.
- Coordinar el tratamiento médico del paciente.
- Indicar alta médica del paciente, que será confirmada posteriormente por administración.


![Vista previa](imagenes%20previas/hospital-9.jpg)

---

## Apps del Proyecto

| App          | Propósito                                                                |
|--------------|--------------------------------------------------------------------------|
| `controlUsuario`   | Gestiona usuarios, roles y autenticación.                     |
| `hospital_pacientes`    |  Gestiona las acciones y datos de los pacientes: turnos, historial clínico y menores a cargo.                                   |
| `hospital_personal`     | Gestiona acciones y datos del personal hospitalario según su rol (superadmin, médicos, enfermeros, etc.).  |
| `intermedio`     | Permite que pacientes y médicos accedan al mismo estudio según corresponda a cada uno.    |

---

## Tecnologías Utilizadas

| Tecnología       | Descripción                                      |
|------------------|--------------------------------------------------|
| Django           | Framework backend principal                      |
| SQLite           | Base de datos        |
| HTML/CSS         | Maquetación responsive y diseño visual adaptable. |
| JavaScript       | Funcionalidades personalizadas del lado del cliente. |

---

## Instalación y configuración
Sigue estos pasos para levantar el proyecto en tu entorno local:

1. **Instalar dependencias**
```bash
 pip install -r requirements.txt
```

3. **Configurar la base de datos**
Crear una base de datos MySQL local (si aún no existe):
CREATE DATABASE hospitalBD;

Actualizar los datos de conexión en settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hospitalBD',
        'USER': '<usuario>',
        'PASSWORD': '<contraseña>',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

4. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Cargar datos iniciales**
Asegúrate de crear la base y ejecutar migraciones antes de importar los datos iniciales.
```bash 
mysql -u <usuario> -p hospitalBD < Documentacion/sistema_hospitalario.sql
```

8. **Iniciar el servidor**
```bash
python manage.py runserver
```

---

## Usuarios de prueba

El sistema incluye usuarios de prueba para cada rol con el fin de facilitar la evaluación de las funcionalidades.

| Tipo | Legajo/Email | Contraseña |
|----|--------|-----------|
| Superadministrador | 1000 | Superadmin |
| Administrador | 1213 | Hospital123 |
| Médico de consultorio | 1005 | Hospital123 |
| Médico hospitalario | 1210 | Hospital123 |
| Enfermero | 1206 | Hospital123 |
| Jefe de enfermería | 1212 | Hospital123 |
| Operador de resultados | 1013 | Hospital123 |
| Paciente | maxi22@gmail.com | Hospital123 |

## Nota sobre el inicio de sesión
El sistema valida si un usuario puede iniciar sesión según su horario de trabajo asignado.
Si un usuario no puede ingresar, es probable que esté fuera de su horario permitido.
Para pruebas o desarrollo local, se puede desactivar temporalmente esta restricción comentando la línea correspondiente en `controlUsuario/forms.py` (Linea 42 Aprox).



