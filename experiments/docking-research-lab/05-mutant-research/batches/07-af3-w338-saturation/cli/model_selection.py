"""Read the original receipt plus an explicit, hash-checked AF model exception."""
import hashlib, json
from pathlib import Path

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def load_manifest(batch):
    receipt=batch/'manifests/received-af3.json'
    manifest=json.loads(receipt.read_text())
    override=batch/'manifests/w338c-model-selection.json'
    if override.exists():
        selection=json.loads(override.read_text())
        if selection['receipt_sha256']!=digest(receipt): raise ValueError('AF receipt changed')
        if selection['alias']!='07_w338c' or selection['selected_model']!=1:
            raise ValueError('Unexpected AF model exception')
        job=next(j for j in manifest['jobs'] if j['alias']==selection['alias'])
        if selection['cif']!=job['models'][1]: raise ValueError('AF model source mismatch')
        root=batch.parents[2]
        if digest(root/selection['cif']['path'])!=selection['cif']['sha256']:
            raise ValueError('Selected CIF changed')
        job['selected_model']=1
        job['model_selection_reason']=selection['reason']
    for job in manifest['jobs']:
        active=batch/'run-01'/job['alias']
        marker=active/'af_model_selection.json'
        if marker.exists():
            record=json.loads(marker.read_text())
            if record['af_model']!=job['selected_model'] or record['source']!=job['models'][job['selected_model']]:
                raise ValueError('Active AF model disagrees with selection manifest')
        elif active.exists() and job['selected_model']!=0:
            raise ValueError('Active exception model lacks provenance marker')
    return manifest

def model_note(manifest):
    exceptions=[f"{j['id']}使用AF model_{j['selected_model']}（结构质量例外）" for j in manifest['jobs'] if j['selected_model']!=0]
    return 'AF受体模型：'+('；'.join(exceptions)+'；其余使用model_0。' if exceptions else '全部使用model_0。')+' AF模型编号与Vina pose MODEL分别记录。'
