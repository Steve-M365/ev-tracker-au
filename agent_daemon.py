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
