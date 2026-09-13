"""Distinguish tracked source provenance from unavailable run-time file snapshots."""
import subprocess,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
original=Path('/Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/MICROADAPT/etcGEMs')
manifest=json.loads((H/'inherited_uncommitted_manifest.json').read_text())
inputs=json.loads((H/'input_manifest.json').read_text())
# Only immutable scientific output files; user documentation can evolve independently.
checks={}
for rel,digest in inputs.items():
 if 'calibration_configD_NLDM_recipe_P16_reduced/' in rel or 'trace_red' in rel:
  p=original/rel;checks[rel]=dict(exists=p.exists(),unchanged=p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
paths=['src','configs','strains/eciML1515/strain.yaml','reports/P6_convergence/p6_fits.py','reports/P11_nested/prior_transform.py','reports/P16_reduced/reduced.py','reports/P16_reduced/run_reduced.py']
changed=subprocess.check_output(['git','diff','--name-only','ab77189','191b4b0','--']+paths,cwd=R,text=True).splitlines()
result=dict(original_output_hash_checks=checks,tracked_source_changes_between_pre_run_and_base=changed,
 limitation='No complete per-file hash snapshot was captured while both P16 workers loaded their modules. Git and startup logs support reconstruction; they cannot rule out a transient uncommitted edit reverted during a run. Current installed library hashes do not establish historical environment identity.',
 local_reporting_patch='run_reduced.py now stores actual pre-final-live dlogz; historical summaries and checkpoints are unchanged.')
(H/'provenance_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert all(v['unchanged'] for v in checks.values())
