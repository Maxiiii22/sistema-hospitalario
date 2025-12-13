from django.urls import path
from . import views 

urlpatterns = [
    path('resultado/<int:resultado_id>/', views.ver_pdf_estudio, name='ver_pdf_estudio'),
]