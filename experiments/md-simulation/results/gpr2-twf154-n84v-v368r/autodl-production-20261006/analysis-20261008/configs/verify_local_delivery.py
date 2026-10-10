"""Verify every recovered immutable small file against its E2 manifest row."""
from pathlib import Path
import csv,hashlib,sys
base=Path(sys.argv[1]); manifest=list(csv.DictReader((base/'evidence/e2_artifacts.tsv').open(),delimiter='\t'))
rows=[]
for item in manifest:
 rel=item['relative_path']
 if rel.startswith('_shared/source_v3/'):
  path=base/'configs/deployed_source_v3'/rel.split('_shared/source_v3/',1)[1]
 elif rel.startswith('_shared/source/'):
  path=base/'configs/deployed_source_v2'/rel.split('_shared/source/',1)[1]
 elif rel.startswith('_comparison/'):
  path=base/'comparison'/rel.split('/',1)[1]
 else:
  path=base/'e2_delivery'/rel
 if rel.endswith('.xtc'):
  continue
 exists=path.is_file()
 observed=hashlib.sha256(path.read_bytes()).hexdigest() if exists else ''
 rows.append({'relative_path':rel,'local_path':str(path),'expected_bytes':item['bytes'],'expected_sha256':item['sha256'],'observed_sha256':observed,'status':'PASS' if exists and path.stat().st_size==int(item['bytes']) and observed==item['sha256'] else 'FAIL'})
with (base/'evidence/local_delivery_validation.tsv').open('w') as stream:
 writer=csv.DictWriter(stream,fieldnames=list(rows[0]),delimiter='\t');writer.writeheader();writer.writerows(rows)
print('recovered_files',len(rows),'passed',sum(row['status']=='PASS' for row in rows))
if any(row['status']!='PASS' for row in rows):raise SystemExit(1)
