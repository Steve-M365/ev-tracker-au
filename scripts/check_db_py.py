import sqlite3
DB='workspace/ev_tracker.db'
conn=sqlite3.connect(DB)
c=conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print('tables:', [r[0] for r in c.fetchall()])
for t in ['price_history','full_market','upcoming_models','alerts']:
    try:
        c.execute(f'SELECT * FROM {t} LIMIT 3;')
        print(t, 'rows:', c.fetchall())
    except Exception as e:
        print(t, 'error:', e)
