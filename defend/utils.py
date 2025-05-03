import json, csv
from .models import (
    DefendMatrix, DefendCoverageEntry,
    DetectionMatrix, DetectionCoverageEntry
)
from cti.models import Technique, TelemetrySource

def import_d3fend_matrix(path, name, description):
    cad = json.load(open(path, encoding='utf-8'))
    matrix = DefendMatrix.objects.create(name=name, description=description)
    tech_map, ctrl_map = {}, {}
    for node in cad.get('nodes', []):
        d3f = node.get('data', {}).get('d3f_class')
        lbl = node.get('data', {}).get('label', '')
        if node['type']=='attack-node' and d3f:
            tid = d3f.split(':')[-1]
            try:
                tech_map[node['id']] = Technique.objects.get(mitre_id=tid)
            except Technique.DoesNotExist:
                continue
        elif node['type']=='countermeasure-node' and d3f:
            cid = d3f.split(':')[-1]
            ctrl_map[node['id']], _ = TelemetrySource.objects.get_or_create(name=cid, defaults={'description':lbl})
    count=0
    for e in cad.get('edges', []):
        if e.get('data',{}).get('d3f_property','').endswith('counteracts'):
            tech=tech_map.get(e['source'])
            ctrl=ctrl_map.get(e['target'])
            if tech and ctrl:
                DefendCoverageEntry.objects.create(
                    matrix=matrix, technique=tech,
                    telemetry_source=ctrl, coverage=1.0
                ); count+=1
    return matrix

def import_detection_matrix(path, source_name, name, description):
    ts = TelemetrySource.objects.get(name=source_name)
    matrix = DetectionMatrix.objects.create(name=name, description=description)
    if path.lower().endswith('.csv'):
        rows = list(csv.DictReader(open(path, encoding='utf-8', newline='')))
    else:
        data = json.load(open(path, encoding='utf-8'))
        rows = [{'mitre_id':t['techniqueID'],'coverage':t.get('value',t.get('score',0))}
                for t in data.get('techniques',[])]
    count=0
    for r in rows:
        tech = Technique.objects.get(mitre_id=r['mitre_id'])
        cov  = float(r['coverage'])
        DetectionCoverageEntry.objects.create(
            matrix=matrix, technique=tech,
            telemetry_source=ts, coverage=cov
        ); count+=1
    return matrix
