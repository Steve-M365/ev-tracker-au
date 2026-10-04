# Email alert (placeholder)
# Requires: user email in ~/.config/email_config or env EMAIL_TO
# Sends when new rows added to price_history or alerts triggered
import sqlite3, os, datetime
DB = "/home/a-steve/workspace/ev_tracker.db"
# Check latest price change
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT model, variant, price_aud, recorded_date FROM price_history ORDER BY recorded_date DESC LIMIT 5")
rows = c.fetchall()
print("Latest prices (alert content):", rows)
