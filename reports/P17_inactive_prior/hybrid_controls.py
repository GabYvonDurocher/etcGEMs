"""D47 bounded development batch; no real-model calls."""
import argparse
import json
import signal
import time
import independence_controls as c
from hybrid_kernel import HybridSampler

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--benchmark',action='store_true');args=parser.parse_args()
    c.HERE=c.c.HERE/'hybrid_controls';c.HERE.mkdir(exist_ok=True)
    c.IndependenceSampler=HybridSampler
    def expired(*unused):raise TimeoutError('D47 diagnostic deadline; checkpoint preserved')
    signal.signal(signal.SIGALRM,expired);start=time.monotonic()
    if not args.benchmark:
        assert json.loads((c.HERE/'spike_17752/result.json').read_text())['wall_s']<180
    for seed in ([17752] if args.benchmark else [17751,17753,17754,17755]):
        remaining=900-(time.monotonic()-start)
        if remaining<=0:raise TimeoutError('D47 batch cap')
        signal.alarm(max(1,int(min(180,remaining))))
        c.run('spike',seed)
        path=c.HERE/f'spike_{seed}/result.json';row=json.loads(path.read_text())
        row.update(kernel='32 global MH attempts plus one random-order coordinate slice sweep',
                   stalled_fraction_scope='Global stage only; local sweep follows even when global stage stalls.',
                   ncall_scope='Library evaluation accounting includes out-of-cube slice proposals.')
        path.write_text(json.dumps(row,indent=2));signal.alarm(0)
