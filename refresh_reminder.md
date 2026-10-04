# Auto-Refresh Reminder — Daily 07:00

- Price DB: ev_tracker.db (price_history, full_market, upcoming_models)
- Rate file: comparison_rates.md — verify car/green/home loan rates
- Sales/FBT: alerts.html — check Kia/BYD offers; confirm ATO LCT threshold ($89,332 FY25-26); verify FBT exemption eligibility per model
- Sources to re-check: thebeep.com.au, kia.com.au, tesla.com/au, carexpert.com.au, drive.com.au, RateCity/Canstar, ATO/treasury.gov.au
- Log: refresh_log.txt, refresh_cron.log


## Automation Status (post-setup)
- Daily cron: 07:00 (refresh + DB check + email stub + deploy server check)
- Manual steps remaining: set EMAIL_TO in email_config.md; run deploy.sh for GitHub Pages; enable SMTP in email_alert.py.
