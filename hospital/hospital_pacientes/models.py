from django.db import models

class Paciente(models.Model):
    persona = models.OneToOneField('controlUsuario.Persona', on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    numero_paciente = models.CharField(max_length=10, unique=True, blank=True, null=True)  # Quitar el blank=True y el null=True al finalizar la BD

    def save(self, *args, **kwargs):
        # Generar número de paciente si no existe
        if not self.numero_paciente:
            self.numero_paciente = f"PAC{self.id or ''}"
        super().save(*args, **kwargs)    
    
    @property
    def tutor(self):
        try:
            return self.responsable.adulto  # relación inversa desde OneToOneField en MenorACargoDePaciente
        except:
            return None    
    
    def __str__(self):
        tutor = self.tutor
        if tutor:
            paciente_info = f"Paciente: {self.id} - {self.persona.get_full_name()} - DNI: {self.persona.dni} | Tutor: {tutor}"
        else:
            paciente_info = f"Paciente: {self.id} - {self.persona.get_full_name()} - DNI: {self.persona.dni} - Email: {self.persona.login_id}"
        return paciente_info


class MenorACargoDePaciente(models.Model):
    PARENTESCO_CHOICES = [
        ('HIJO', 'Hijo/a'),
        ('NIETO', 'Nieto/a'),
        ('SOBRINO', 'Sobrino/a'),
        ('ABUELO', 'Abuelo/a'),
        ('HERMANO', 'Hermano/a mayor'),
        ('TUTOR_LEGAL', 'Tutor Legal'),
    ]  
    
    menor = models.OneToOneField(Paciente,on_delete=models.CASCADE,related_name='responsable')
    adulto = models.ForeignKey(Paciente, on_delete=models.CASCADE,related_name="menores_a_cargo")
    parentesco = models.CharField(max_length=50,choices=PARENTESCO_CHOICES,verbose_name="Parentesco con el menor")   
    
    def __str__(self):
        return f"{self.menor.persona.get_full_name()} con el DNI: {self.menor.persona.dni} esta a cargo de {self.adulto.persona.get_full_name()} con el DNI: {self.adulto.persona.dni} - Parentesco con el menor: {self.get_parentesco_display()}"
