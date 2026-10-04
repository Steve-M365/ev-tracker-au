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
        build_html()
        f.write(f"  Next cycle in 60s\n")


def build_html():
    """Regenerate HTML pages from DB data."""
    import sqlite3, re
    DB = "/home/a-steve/workspace/ev_tracker.db"
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # all_vehicles.html
    c.execute("SELECT DISTINCT brand, model, body, range_km, battery_kwh, dc_peak, price_from, notes FROM full_market ORDER BY brand, model")
    rows = c.fetchall()
    table_rows = []
    for r in rows:
        brand, model, body, range_km, battery_kwh, dc_peak, price_from, notes = r
        table_rows.append(f'<tr data-brand="{brand}"><td><span class="model">{brand} {model}</span> <span class="tag">{body}</span></td><td>{"~$" + str(price_from) if price_from else "TBA"}</td><td>{str(range_km) if range_km else "TBA"} km</td><td>{str(dc_peak) if dc_peak else "TBA"} kW</td><td>8yr (est)</td><td>{notes or ""}</td></tr>')
    with open("/home/a-steve/workspace/all_vehicles.html") as f:
        html = f.read()
    tbody_match = re.search(r"<tbody>.*?</tbody>", html, re.DOTALL)
    if tbody_match:
        new_tbody = "<tbody>\n" + "".join(table_rows) + "\n</tbody>"
        html = html.replace(tbody_match.group(0), new_tbody)
        with open("/home/a-steve/workspace/all_vehicles.html", "w") as f:
            f.write(html)
    # compare.html dropdown
    c.execute("SELECT DISTINCT brand, model FROM full_market ORDER BY brand, model")
    vehicles = [f"{r[0]} {r[1]}" for r in c.fetchall()]
    options_html = "".join([f'<option value="{v}">{v}</option>' for v in vehicles])
    with open("/home/a-steve/workspace/compare.html") as f:
        comp = f.read()
    for sid in ["v1", "v2", "v3"]:
        comp = re.sub(rf'(<select id="{sid}"[^>]*>)(.*?)(</select>)', r'\1' + options_html + r'\3', comp, flags=re.DOTALL)
    with open("/home/a-steve/workspace/compare.html", "w") as f:
        f.write(comp)
    # alerts.html from DB
    c.execute("SELECT trigger_type, message, status FROM alerts WHERE status='open'")
    alerts = c.fetchall()
    alert_cards = []
    for a in alerts:
        t, m, s = a
        alert_cards.append(f'<div class="alert-card"><h3>{t}</h3><p>{m}</p></div>')
    with open("/home/a-steve/workspace/alerts.html") as f:
        al = f.read()
    body_match = re.search(r'<div class="container">.*?</div>\s*</body>', al, re.DOTALL)
    if body_match:
        new_body = '<div class="container">\n' + "\n".join(alert_cards) + '\n</div>\n</body>'
        al = al.replace(body_match.group(0), new_body)
        with open("/home/a-steve/workspace/alerts.html", "w") as f:
            f.write(al)
    with open(LOG, "a") as logf:
        logf.write(f"[{datetime.datetime.now()}] Rebuilt all_vehicles ({len(rows)}), compare ({len(vehicles)}), alerts ({len(alerts)})\n")
    # Update index.html DB count snippet
    try:
        with open("/home/a-steve/workspace/index.html") as f:
            idx = f.read()
        idx = idx.replace("83 verified models", f"{len(rows)} verified models")
        idx = idx.replace("5 price records", f"{c.execute('SELECT COUNT(*) FROM price_history').fetchone()[0]} price records")
        with open("/home/a-steve/workspace/index.html", "w") as f:
            f.write(idx)
    except Exception:
        pass


if __name__ == "__main__":
    while True:
        run()
        time.sleep(60)
        # Auto-sync to GitHub
        import subprocess, os
        try:
            last_sync = "/home/a-steve/workspace/.last_git_sync"
            try:
                if not os.path.exists(last_sync) or (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(last_sync))).days >= 1:
                    subprocess.run(["git", "add", "-A"], cwd="/home/a-steve/workspace", check=True, capture_output=True)
                    subprocess.run(["git", "commit", "-m", "Agent daily sync: DB + pages update"], cwd="/home/a-steve/workspace", check=False, capture_output=True)
                    subprocess.run(["git", "push", "origin", "main"], cwd="/home/a-steve/workspace", check=False, capture_output=True)
                    with open(last_sync, "w") as syncf: syncf.write(str(datetime.datetime.now()))
            except Exception as e:
                with open(LOG, "a") as logf: logf.write(f"[{datetime.datetime.now()}] Git sync error: {e}\n")
        except Exception as e:
            with open(LOG, "a") as logf:
                logf.write(f"[{datetime.datetime.now()}] Git sync error: {e}\n")
