"""Verify enforced control deadline without starting an expensive sampler."""
import controls as c
from types import SimpleNamespace
import time,json
original=c._run
try:
    c._run=lambda *args:time.sleep(3)
    t=time.monotonic()
    try:c.run(SimpleNamespace(seconds=1,kind='deadline_test',kernel='unit'),0,None)
    except TimeoutError:pass
    else:raise AssertionError('deadline failed to interrupt')
    elapsed=time.monotonic()-t
    assert elapsed<2,elapsed
    print(json.dumps(dict(passed=True,elapsed_s=elapsed)))
finally:c._run=original
