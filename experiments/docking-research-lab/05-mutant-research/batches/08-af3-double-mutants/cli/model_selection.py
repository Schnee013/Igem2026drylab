"""Batch08 receipt validation: 18 designed double mutants, AF model_0."""
import hashlib,json

def load_manifest(batch):
    design_path=batch/'manifests/double-mutants.json'
    design=json.loads(design_path.read_text())
    m=json.loads((batch/'manifests/received-af3.json').read_text())
    if m['status']!='validated' or m['design_sha256']!=hashlib.sha256(design_path.read_bytes()).hexdigest():
        raise ValueError('Unvalidated or changed design')
    expected={r['id']:r['af_job_name'] for r in design['variants']}
    if len(m['jobs'])!=18 or {j['id']:j['alias'] for j in m['jobs']}!=expected:
        raise ValueError('Batch08 receipt/design coverage mismatch')
    for j in m['jobs']:
        if j['selected_model']!=0: raise ValueError('Expected AF model_0')
        marker=batch/'run-01'/j['alias']/'af_model_selection.json'
        if marker.exists():
            rec=json.loads(marker.read_text())
            if rec['af_model']!=0 or rec['source']!=j['models'][0]:
                raise ValueError('AF model provenance mismatch')
    return m

def model_note(manifest):
    return 'AF model_0; minimum-score Vina pose selected separately.'
