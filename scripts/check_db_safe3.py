import sqlite3
conn = sqlite3.connect('workspace/ev_tracker.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print('Tables:', [r[0] for r in cursor.fetchall()])
for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall():
    tn = t[0]
    cursor.execute(f"SELECT COUNT(*) FROM {tn}")
    print(f'{tn}: {cursor.fetchone()[0]}')
