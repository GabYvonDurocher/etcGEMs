"""T1 -- a tested SIGALRM deadline (RIGOUR 8). A timeout raises Deadline; the caller records it
as an UNRESOLVED outcome and never restarts without limit."""
import signal, contextlib, time


class Deadline(Exception):
    pass


@contextlib.contextmanager
def deadline(seconds: float, label: str = ""):
    def _h(signum, frame):
        raise Deadline(f"deadline {seconds}s exceeded: {label}")
    old = signal.signal(signal.SIGALRM, _h)
    signal.setitimer(signal.ITIMER_REAL, float(seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def self_test():
    """must be run before first use; both branches exercised."""
    t0 = time.time()
    try:
        with deadline(0.5, "self-test long"):
            time.sleep(2.0)
        raise SystemExit("alarm self-test FAILED: long sleep did not raise")
    except Deadline:
        dt = time.time() - t0
        assert dt < 1.5, f"raised too late: {dt:.2f}s"
    with deadline(1.0, "self-test short"):
        time.sleep(0.1)
    print(f"[alarm] self-test PASS: 2.0 s sleep raised at {dt:.2f} s under a 0.5 s deadline; "
          f"0.1 s sleep passed under 1.0 s")
    return True


if __name__ == "__main__":
    self_test()
