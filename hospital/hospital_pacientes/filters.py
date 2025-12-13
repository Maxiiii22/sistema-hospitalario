import django_filters
from hospital_personal.models import Consultas
from django import forms
from datetime import datetime,time

class ConsultasFilter(django_filters.FilterSet):
    turno__especialidad__nombre_especialidad = django_filters.CharFilter(
        field_name='turno__especialidad__nombre_especialidad',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Especialidad:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por especialidad...'})
    )    
    fecha = django_filters.DateFilter(
        method='filtrar_por_fecha',
        label='Fecha de la consulta:',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Consultas
        fields = [
            'turno__especialidad',  
            'fecha'  
        ]
        
        
    def filtrar_por_fecha(self, queryset, name, value):  # Agregamos este metodo porque Django trata los campos con auto_now_add como: solo de creación, no editables y no filtrables directamente a menos que lo fuerces. Por eso este metodo resuelve el problema
        if value:
            inicio = datetime.combine(value, time.min)
            fin = datetime.combine(value, time.max)
            return queryset.filter(fecha__range=(inicio, fin))
        return queryset            
