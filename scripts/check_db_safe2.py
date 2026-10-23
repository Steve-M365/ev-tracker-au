import sqlite3
conn = sqlite3.connect('workspace/ev_tracker.db')
for t in ['scans','models','price_history','alerts','incentives']:
    c = conn.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t}: {c.fetchone()[0]}')
print('price_history:')
for r in conn.execute('SELECT * FROM price_history').fetchall():
    print(' ', r)
print('alerts:')
for r in conn.execute('SELECT trigger_type,status FROM alerts').fetchall():
    print(' ', r)
