"""D33: finish registered third trace, validate it, then execute registered D32."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATUS = HERE/'finish_third_status.json'


def state(status, **kwargs):
    STATUS.write_text(json.dumps(dict(status=status, pid=os.getpid(), **kwargs), indent=2))


def launch(script, args, log_name):
    with (HERE/log_name).open('x') as log:
        process = subprocess.Popen([sys.executable, str(HERE/script)]+args,
            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        state('running bounded child', script=script, child_pid=process.pid)
        try:
            code = process.wait(timeout=1980)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            raise TimeoutError(f'{script} exceeded cleanup allowance')
        if code != 0:
            raise RuntimeError(f'{script} exited {code}')


def main():
    with (HERE/'finish_third.claim').open('x') as out:
        out.write(str(os.getpid()))
    try:
        previous = json.loads((HERE/'conditional_17513/status.json').read_text())
        assert previous['status'] == 'timed out; last safe checkpoint preserved'
        launch('conditional_trace.py', ['--seed', '17513', '--resume', '--seconds', '1800', '--iterations', '2500'],
               'conditional_17513_resume.log')
        final = json.loads((HERE/'conditional_17513/status.json').read_text())
        if final['status'] != 'completed diagnostic iterations':
            raise RuntimeError('Third trace did not complete; do not launch geometry test')
        from audit_conditional_trace import audit
        result = audit(HERE/'conditional_17513')
        assert result['iterations'] == 2500 and result['accepted_traced'] == 2500
        with (HERE/'conditional_17513/completed_audit.json').open('x') as out:
            json.dump(result, out, indent=2)
        state('third trace audited; launching registered geometry test')
        launch('axis_probe.py', [], 'axis_probe.log')
        final = json.loads((HERE/'axis_probe/status.json').read_text())
        assert final['status'] == 'completed six proposals'
        state('registered batches completed; causal interpretation pending')
    except Exception as error:
        state('stopped for review; no subsequent child dispatched', error=repr(error))
        raise


if __name__ == '__main__':
    main()
