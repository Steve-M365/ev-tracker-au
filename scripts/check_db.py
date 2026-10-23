#!/usr/bin/env python3
import sqlite3, os
conn = sqlite3.connect('workspace/ev_tracker.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print('tables:', cursor.fetchall())
cursor.execute("PRAGMA table_info(price_history)")
print('price_history schema:', cursor.fetchall())
cursor.execute('SELECT * FROM price_history LIMIT 5')
print('price_history rows:', cursor.fetchall())
cursor.execute("SELECT * FROM alerts")
print('alerts:', cursor.fetchall())
cursor.execute('SELECT COUNT(*) FROM full_market')
print('full_market count:', cursor.fetchone()[0])
