from django import forms
from defend.models import DefendMatrix, DetectionMatrix

# заглушки; расширите при желании
class ContextForm(forms.Form):
    sectors = forms.MultipleChoiceField(
        required=False, choices=[("bank", "Банки"), ("fintech", "FinTech")]
    )
    regions = forms.MultipleChoiceField(
        required=False, choices=[("RU", "Россия"), ("EU", "Европа")]
    )
    sources = forms.MultipleChoiceField(
        required=False, choices=[("edr", "EDR"), ("siem", "SIEM")]
    )


class MatrixUploadForm(forms.Form):
    name_d3fend = forms.CharField(required=False, label="Имя D3FEND")
    d3fend_json = forms.FileField(required=False, label="D3FEND-JSON")

    name_detect = forms.CharField(required=False, label="Имя detection")
    detect_file = forms.FileField(required=False, label="Heatmap JSON/CSV")


class AnalysisForm(forms.Form):
    defend_matrix = forms.ModelChoiceField(
        queryset=DefendMatrix.objects.all(), label="D3FEND"
    )
    detect_matrix = forms.ModelChoiceField(
        queryset=DetectionMatrix.objects.all(), label="Detection"
    )
