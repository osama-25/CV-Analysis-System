from django import forms
from .models import CVDocument

class CVUploadForm(forms.ModelForm):
    class Meta:
        model = CVDocument
        fields = ('file',)
