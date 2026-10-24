import sqlite3
c = sqlite3.connect('workspace/ev_tracker.db').cursor()
for t in ['full_market','price_history','upcoming_models','alerts']:
    c.execute(f"SELECT count(*) FROM {t}")
    print(f"{t}: {c.fetchone()[0]}")
c.execute("SELECT count(*) FROM alerts WHERE status='open'")
print("open_alerts:", c.fetchone()[0])
