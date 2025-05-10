# defend/views.py
import io
import json                                   # ←  json нужен для json.load
from collections import defaultdict

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command

from .forms import ContextForm, MatrixUploadForm, AnalysisForm
from .models import DefendMatrix, DetectionMatrix
from .utils import import_d3fend_matrix, import_detection_matrix   # ←  сигнатуры «file_obj»

# ─────────────────── UI ────────────────────
def home_view(request):
    return render(request, "home.html")


def select_context_view(request):
    """
    Страница, где пользователь отмечает секторы, регионы и источники.
    """
    if request.method == "POST":
        form = ContextForm(request.POST)
        if form.is_valid():
            for k in ("sectors", "regions", "sources"):
                request.session[k] = list(form.cleaned_data[k])
            messages.success(request, "Контекст сохранён")
            return redirect("upload-matrices")
    else:
        form = ContextForm()

    return render(request, "defend/context.html", {"form": form})


# ───────────── Загрузка матриц ─────────────
def upload_matrices_view(request):
    """
    Принимаем JSON-файл D3FEND и / или слой Detection (Navigator-layer).
    """
    if request.method == "POST":
        form = MatrixUploadForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data

            # D3FEND
            if cd["d3fend_json"]:
                d3 = DefendMatrix.objects.create(
                    name=cd["name_d3fend"] or cd["d3fend_json"].name
                )
                import_d3fend_matrix(file_obj=cd["d3fend_json"], matrix=d3)
                messages.success(request, f"D3FEND «{d3.name}» загружена")

            # Detection
            if cd["detect_file"]:
                det = DetectionMatrix.objects.create(
                    name=cd["name_detect"] or cd["detect_file"].name
                )
                import_detection_matrix(file_obj=cd["detect_file"], matrix=det)
                messages.success(request, f"Detection «{det.name}» загружена")

            return redirect("results")
    else:
        form = MatrixUploadForm()

    return render(request, "defend/upload_matrices.html", {"form": form})


# ───────────── Результаты анализа ──────────
def results_view(request):
    """
    Запускаем management-команду run_analysis и красиво выводим,
    сначала группировки, потом процедуры.
    """
    if request.method == "POST":
        form = AnalysisForm(request.POST)
        if form.is_valid():
            dm = form.cleaned_data["detect_matrix"].name
            fm = form.cleaned_data["defend_matrix"].name

            sectors = request.session.get("sectors", [])
            regions = request.session.get("regions", [])
            sources = request.session.get("sources", [])

            # ─── формируем CLI-аргументы ───
            extra = []
            for flag, coll in [("sector", sectors), ("region", regions), ("sources", sources)]:
                for obj in coll:
                    extra += [f"--{flag}", getattr(obj, "name", str(obj))]

            buf = io.StringIO()
            call_command(
                "run_analysis",
                "--detect-matrix", dm,
                "--defend-matrix", fm,
                *extra,
                stdout=buf,
            )

            lines = buf.getvalue().splitlines()
            headline = lines[0] if lines else "-"
            rows = []
            for row in lines[1:]:
                g, p, t, *rest = row.split(",")
                kv = dict(x.split("=") for x in rest)
                rows.append({
                    "group": g,
                    "procedure": p,
                    "technique": t,
                    "detect_cov": float(kv["detect_cov"]),
                    "defend_cov": float(kv["defend_cov"]),
                    "score": float(kv["score"]),
                })

            # сортировка: группы по максимуму score, внутри – по score
            grp_score = defaultdict(float)
            for r in rows:
                grp_score[r["group"]] = max(grp_score[r["group"]], r["score"])
            order = sorted(grp_score, key=lambda g: -grp_score[g])
            rows.sort(key=lambda r: (order.index(r["group"]), -r["score"]))

            return render(request, "defend/results.html", {
                "total": headline,
                "groups": order,
                "results": rows,
            })
    else:
        form = AnalysisForm()

    return render(request, "defend/results.html", {"form": form, "results": None})
