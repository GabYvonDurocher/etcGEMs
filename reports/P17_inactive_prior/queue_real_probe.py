"""Launch the preregistered real probe only after all analytical replicas finish."""
from pathlib import Path
import subprocess,sys,time,json
H=Path(__file__).resolve().parent
start=time.monotonic();needed=[H/f'spike_plain_p1_t0_s3_{k}_global-coordinate.json' for k in range(17001,17006)]
while not all(p.exists() for p in needed):
    if time.monotonic()-start>1800:raise RuntimeError('Analytical batch did not finish within queue budget; real probe not launched')
    time.sleep(5)
# Results are written after completed integration, arrays and metrics. No extra fit
# or adaptive parameter choice is made here: D11 fixed the six probes in advance.
(H/'queue_real_probe_state.json').write_text(json.dumps({'status':'running real probe','wait_s':time.monotonic()-start},indent=2))
with (H/'real_kernel_probe.log').open('w') as log:
    result=subprocess.run([sys.executable,str(H/'real_kernel_probe.py')],cwd=H.parents[1],stdout=log,stderr=subprocess.STDOUT)
(H/'queue_real_probe_state.json').write_text(json.dumps({'status':'finished','exit_code':result.returncode,'wall_s':time.monotonic()-start},indent=2))
sys.exit(result.returncode)
