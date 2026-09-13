"""Finish the three registered D20 diagnostics sequentially; never a posterior fit."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATUS = HERE / 'conditional_batch_status.json'


def record(state, **details):
    STATUS.write_text(json.dumps(dict(state=state, pid=os.getpid(), **details), indent=2))


def verify(seed):
    folder = HERE / f'conditional_{seed}'
    status = json.loads((folder / 'status.json').read_text())
    if status['status'] != 'completed diagnostic iterations':
        raise RuntimeError(f'Seed {seed} needs review: {status["status"]}')
    from audit_conditional_trace import audit
    result = audit(folder)
    if result['iterations'] != 2500 or result['accepted_traced'] != 2500:
        raise RuntimeError(f'Seed {seed} did not complete the registered trace')
    # Validity depends on accounting and completion, never the direction of drift.
    with (folder / 'completed_audit.json').open('x') as out:
        json.dump(result, out, indent=2)
    return result


def main():
    # Exclusive claim prevents a heartbeat or second invocation duplicating the batch.
    claim = HERE / 'conditional_batch.claim'
    with claim.open('x') as out:
        out.write(str(os.getpid()))
    try:
        record('waiting for existing seed 17511; no additional sampler running')
        deadline = time.monotonic() + 3600
        while not (HERE / 'conditional_17511' / 'status.json').exists():
            if time.monotonic() >= deadline:
                raise TimeoutError('Existing seed has not written a terminal status; review required')
            time.sleep(30)
        results = [verify(17511)]
        for seed in [17512, 17513]:
            if (HERE / f'conditional_{seed}').exists():
                raise FileExistsError(f'Seed {seed} already exists; review before continuing')
            record('running registered conditional diagnostic', seed=seed)
            with (HERE / f'conditional_{seed}.log').open('x') as log:
                child = subprocess.Popen(
                    [sys.executable, str(HERE / 'conditional_trace.py'),
                     '--seed', str(seed), '--seconds', '7200', '--iterations', '2500'],
                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                    start_new_session=True)
                record('running registered conditional diagnostic', seed=seed, child_pid=child.pid)
                try:
                    code = child.wait(timeout=7380)
                except subprocess.TimeoutExpired:
                    # Backup process-group limit if sampler/pool cleanup hangs.
                    import signal
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                        child.wait()
                    raise TimeoutError(f'Seed {seed} exceeded cleanup allowance; stopped for review')
            if code != 0:
                raise RuntimeError(f'Seed {seed} exited {code}; review required')
            results.append(verify(seed))
        record('registered diagnostics completed; causal assessment still required',
               iterations=[r['iterations'] for r in results])
    except Exception as error:
        record('stopped for diagnostic review; no subsequent seed launched', error=repr(error))
        raise


if __name__ == '__main__':
    main()
