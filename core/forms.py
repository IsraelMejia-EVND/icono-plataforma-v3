from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import PerfilEstilo, Usuario, Cita

from django import forms

class RegistroClienteForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username",)

class ComentarioForm(forms.Form):
    calificacion = forms.IntegerField(label=_("Calificación (1 a 5)"), min_value=1, max_value=5)
    texto = forms.CharField(
        label=_("Comentario"),
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

class PerfilEstiloForm(forms.ModelForm):
    class Meta:
        model = PerfilEstilo
        fields = ("tendencia_preferida", "objetivo")
        labels = {
            "tendencia_preferida": _("Tendencia preferida"),
            "objetivo": _("¿Qué buscas en una asesoría?"),
        }
        widgets = {
            "objetivo": forms.Textarea(attrs={"rows": 3}),
        }

class SolicitudCitaForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        label=_("Fecha y hora de la cita (Tijuana)"),
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Cita
        fields = ("asesor", "fecha_hora")

    def __init__(self, *args, cliente, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asesor"].label = _("Asesor")
        self.fields["asesor"].queryset = (
            Usuario.objects.filter(groups__name="Asesor", is_active=True)
            .exclude(pk=cliente.pk)
            .order_by("username")
        )

    def clean_fecha_hora(self):
        fecha_hora = self.cleaned_data["fecha_hora"]
        if fecha_hora <= timezone.now():
            raise forms.ValidationError(_("Elige una fecha y hora futuras."))
        return fecha_hora