import sqlite3
DB = '/home/a-steve/workspace/ev_tracker.db'
conn = sqlite3.connect(DB)
for t in ['price_history','full_market','alerts','upcoming_models']:
    try:
        c = conn.execute('SELECT COUNT(*) FROM ' + t)
        print(t + ': ' + str(c.fetchone()[0]))
    except Exception as e:
        print(t + ': MISSING - ' + str(e))
print('--- price_history last 3 ---')
for r in conn.execute('SELECT * FROM price_history ORDER BY rowid DESC LIMIT 3').fetchall():
    print(r)
print('--- alerts ---')
for r in conn.execute('SELECT * FROM alerts').fetchall():
    print(r)
print('--- upcoming_models ---')
for r in conn.execute('SELECT * FROM upcoming_models').fetchall():
    print(r)
