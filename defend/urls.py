# defend/urls.py
from django.urls import path

from .views import (
    home_view,
    select_context_view,
    upload_matrices_view,
    results_view,
)

urlpatterns = [
    path("", home_view, name="home"),                       #  /
    path("context/", select_context_view, name="select-context"),   #  /context/
    path("matrices/upload/", upload_matrices_view, name="upload-matrices"),
    path("results/", results_view, name="results"),
]
