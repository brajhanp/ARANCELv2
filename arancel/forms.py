from django import forms
from .models import Seccion
 
class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre', 'descripcion'] 