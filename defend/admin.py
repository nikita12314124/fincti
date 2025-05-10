# defend/admin.py
import io

from django import forms
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.core.management import call_command

from .models import DefendMatrix, DetectionMatrix
from cti.models import Sector, Region, TelemetrySource


# ─────────── форма, та же что была ───────────
class AnalysisForm(forms.Form):
    sector = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple, label="Сектора"
    )
    region = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple, label="Регионы"
    )
    sources = forms.ModelMultipleChoiceField(
        queryset=TelemetrySource.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple, label="Источники телеметрии"
    )
    detect_matrix = forms.ModelChoiceField(
        queryset=DetectionMatrix.objects.all(), required=False,
        label="Матрица Detection"
    )
    defend_matrix = forms.ModelChoiceField(
        queryset=DefendMatrix.objects.all(), required=False,
        label="Матрица D3FEND"
    )


# ─────────── админ DefendMatrix с кнопкой ───────────
@admin.register(DefendMatrix)
class DefendMatrixAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")          # ←  «created_at» действительно есть в модели
    search_fields = ("name",)
    date_hierarchy = "created_at"

    change_list_template = "admin/defend/run_analysis.html"

    # добавляем собственный URL
    def get_urls(self):
        return [
            path(
                "run-analysis/",
                self.admin_site.admin_view(self.run_analysis_view),
                name="defend_run_analysis",
            )
        ] + super().get_urls()

    # сама вьюха
    def run_analysis_view(self, request):
        if request.method == "POST":
            form = AnalysisForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                cli = []
                for flag in ("sector", "region", "sources"):
                    for obj in cd[flag]:
                        cli += [f"--{flag}", obj.name]
                if cd["detect_matrix"]:
                    cli += ["--detect-matrix", cd["detect_matrix"].name]
                if cd["defend_matrix"]:
                    cli += ["--defend-matrix", cd["defend_matrix"].name]

                buf = io.StringIO()
                call_command("run_analysis", *cli, stdout=buf)
                messages.success(request, buf.getvalue().replace("\n", "<br>"))
                return redirect("..")
        else:
            form = AnalysisForm()

        return render(request, "admin/defend/run_analysis.html", {"form": form})


# ─────────── DetectionMatrix без лишнего ───────────
@admin.register(DetectionMatrix)
class DetectionMatrixAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")          # uploaded_at → created_at
    search_fields = ("name",)
    date_hierarchy = "created_at"
