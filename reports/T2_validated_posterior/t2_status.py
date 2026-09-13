#!/usr/bin/env python3
"""T2 -- the state file every task and the driver write ATOMICALLY (temp file + os.replace).
Fields (prompt): stage, timestamp, branch, head, runs_complete, runs_audited, driver_pid, last_note,
plus whatever the driver adds (current_run, iteration, dlogz, wall_h, ncall)."""
import os, json, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PATH = os.environ.get("T2_STATUS_PATH") or os.path.join(HERE, "status.json")   # the driver's toy mode redirects this
STAGES = ["task0_done", "task1_done", "task2_done", "task3_done", "driver_running", "driver_finished",
          "driver_stopped", "task5_done", "task6_done"]


def _git(*args):
    try:
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return "?"


def read():
    return json.load(open(PATH)) if os.path.exists(PATH) else None


def write(stage, note="", **extra):
    assert stage in STAGES, stage
    cur = read() or {}
    cur.update(dict(stage=stage, timestamp=datetime.datetime.now().isoformat(timespec="seconds"),
                    branch=_git("branch", "--show-current"), head=_git("rev-parse", "--short", "HEAD"),
                    runs_complete=int(cur.get("runs_complete", 0)), runs_audited=int(cur.get("runs_audited", 0)),
                    driver_pid=cur.get("driver_pid"), last_note=note))
    cur.update(extra)
    tmp = PATH + f".tmp.{os.getpid()}"
    with open(tmp, "w") as fh:
        json.dump(cur, fh, indent=1, default=str); fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, PATH)
    return cur


def stage_index(stage):
    return STAGES.index(stage)


if __name__ == "__main__":
    import sys
    print(json.dumps(read(), indent=1) if len(sys.argv) == 1 else json.dumps(write(sys.argv[1], " ".join(sys.argv[2:])), indent=1))
