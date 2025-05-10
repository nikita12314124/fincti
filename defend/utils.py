import json
import csv
from typing import BinaryIO

from defend.models import (
    DefendMatrix,
    DetectionMatrix,
    DefendCell,
    DetectCell,
)

# ─────────────── D3FEND ────────────────
def import_d3fend_matrix(*, file_obj: BinaryIO, matrix: DefendMatrix) -> None:
    """
    Принимает открытый файл JSON (UploadedFile) и сохраняет defense-measures.
    """
    data = json.load(file_obj)

    for obj in data.get("objects", []):
        if obj.get("type") != "x-defense-measure":
            continue
        tech_id = obj["external_references"][0]["external_id"]
        DefendCell.objects.get_or_create(
            matrix=matrix,
            d3_id=tech_id,
            defaults={"name": obj.get("name", "")},
        )


# ─────────── Detection heatmap ──────────
def import_detection_matrix(*, file_obj: BinaryIO, matrix: DetectionMatrix) -> None:
    """
    navigator-layer (JSON) или CSV с колонками: technique_id,score
    """
    name = getattr(file_obj, "name", "")
    if name.endswith(".json"):
        layer = json.load(file_obj)
        for cell in layer.get("techniques", []):
            DetectCell.objects.get_or_create(
                matrix=matrix,
                technique_id=cell["techniqueID"],
                defaults={"score": float(cell.get("score", 0))},
            )
    else:  # CSV
        reader = csv.DictReader((l.decode() for l in file_obj))
        for row in reader:
            DetectCell.objects.get_or_create(
                matrix=matrix,
                technique_id=row["technique_id"],
                defaults={"score": float(row.get("score", 0))},
            )
