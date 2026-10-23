#!/usr/bin/env bash
# Daily EV tracker refresh: price DB check + rate reminder
DATE=$(date +%Y-%m-%d)
echo "[$DATE] Refresh: check ev_tracker.db pricing & upcoming_models.md; review comparison_rates.md; verify open alerts." >> /home/a-steve/workspace/refresh_log.txt
echo "[$DATE] ACTION: confirm Kia EV5 offer status (kia.com.au), BYD offers (thebeep.com.au), Tesla pricing (tesla.com/au), lender rates (RateCity/Canstar), ATO FBT threshold." >> /home/a-steve/workspace/refresh_log.txt
echo "[$DATE] Open DB: sqlite3 /home/a-steve/workspace/ev_tracker.db 'SELECT * FROM price_history;' >> /home/a-steve/workspace/refresh_log.txt" >> /home/a-steve/workspace/refresh_log.txt
echo "[$DATE] Alerts: $(sqlite3 /home/a-steve/workspace/ev_tracker.db 'SELECT trigger_type, status FROM alerts;')" >> /home/a-steve/workspace/refresh_log.txt

echo "[$DATE] Auto-check DB updates..."
# Trigger email alert if new price rows (stub — requires EMAIL_TO set)
if [ -n "$EMAIL_TO" ]; then
    python3 /home/a-steve/workspace/email_alert.py
    echo "[$DATE] Email alert triggered (stub)"
else
    echo "[$DATE] Email skipped: EMAIL_TO not set"
fi
# Ensure local server running
if ! pgrep -f "python3 -m http.server 8080" > /dev/null; then
    nohup python3 -m http.server 8080 --directory /home/a-steve/workspace > /dev/null 2>&1 &
    echo "[$DATE] Server started on port 8080"
else
    echo "[$DATE] Server already running"
fi
