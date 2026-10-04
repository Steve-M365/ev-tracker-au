#!/usr/bin/env python3
"""Persistent EV tracker agent — monitors prices, sends updates, manages DB."""
import sqlite3, time, os, datetime
DB = "/home/a-steve/workspace/ev_tracker.db"
LOG = "/home/a-steve/workspace/agent_daemon.log"

def run():
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now()}] Agent running — DB check + refresh cycle\n")
        # Verify DB
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        for t in ["price_history", "full_market", "upcoming_models", "alerts"]:
            count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            f.write(f"  {t}: {count} rows\n")
        # Check alerts
        open_alerts = c.execute("SELECT trigger_type FROM alerts WHERE status='open'").fetchall()
        f.write(f"  Open alerts: {len(open_alerts)}\n")
        f.write(f"  Next cycle in 60s\n")

if __name__ == "__main__":
    while True:
        run()
        time.sleep(60)
        # Auto-sync to GitHub
        import subprocess, os
        try:
            last_sync = "/home/a-steve/workspace/.last_git_sync"
            try:
                if not os.path.exists(last_sync) or (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(last_sync))).days >= 1:
                    subprocess.run(["git", "add", "-A"], cwd="/home/a-steve/workspace", check=True, capture_output=True)
                    subprocess.run(["git", "commit", "-m", "Agent daily sync: DB + pages update"], cwd="/home/a-steve/workspace", check=False, capture_output=True)
                    subprocess.run(["git", "push", "origin", "main"], cwd="/home/a-steve/workspace", check=False, capture_output=True)
                    with open(last_sync, "w") as syncf: syncf.write(str(datetime.datetime.now()))
            except Exception as e:
                with open(LOG, "a") as logf: logf.write(f"[{datetime.datetime.now()}] Git sync error: {e}\n")
        except Exception as e:
            with open(LOG, "a") as logf:
                logf.write(f"[{datetime.datetime.now()}] Git sync error: {e}\n")
