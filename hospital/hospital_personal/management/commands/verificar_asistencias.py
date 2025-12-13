from django.core.management.base import BaseCommand
from django.utils import timezone
from hospital_personal.models import Turno, TurnoEstudio

class Command(BaseCommand):
    help = 'Verifica si los turnos han sido asistidos y cambia su estado'

    def actualizar_estado_turno(self, turnos):
        hoy = timezone.now()
        
        for turno in turnos:
            # Obtener el rango de la hora del turno (hora de inicio y hora de fin)
            hora_inicio, hora_fin = turno.obtener_rango_turno()

            # Generamos las fechas completas de inicio y fin con la fecha del turno
            fecha_inicio = timezone.make_aware(
                timezone.datetime.combine(turno.fecha_turno, hora_inicio)
            )
            fecha_fin = timezone.make_aware(
                timezone.datetime.combine(turno.fecha_turno, hora_fin)
            )

            # Si la hora actual está fuera del rango y el paciente no asistió, cambiar estado
            if hoy > fecha_fin and not turno.asistio:
                turno.estado = 'noAsistio'
                turno.save()

    def handle(self, *args, **kwargs):
        # Obtener los turnos pendientes de ambos modelos
        turnos_pendientes = Turno.objects.filter(
            fecha_turno__lt=timezone.now().date(),
            asistio=False,
            estado='pendiente',
        )
        turnosEstudios_pendientes = TurnoEstudio.objects.filter(
            fecha_turno__lt=timezone.now().date(),
            asistio=False,
            estado='pendiente',
        )

        # Actualizar los estados de los turnos
        self.actualizar_estado_turno(turnos_pendientes)
        self.actualizar_estado_turno(turnosEstudios_pendientes)

        self.stdout.write(self.style.SUCCESS('Estado de los turnos actualizado correctamente.'))