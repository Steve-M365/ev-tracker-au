import sqlite3
c = sqlite3.connect('/home/a-steve/workspace/ev_tracker.db').cursor()
c.execute('SELECT * FROM price_history')
print('price_history count:', len(c.fetchall()))
c.execute('SELECT trigger_type, status FROM alerts')
print('alerts:', c.fetchall())
