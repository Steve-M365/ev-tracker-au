import csv
with open('workspace/full_market.csv', newline='') as f:
    rows = list(csv.DictReader(f))
print('Rows:', len(rows))
print('Columns:', list(rows[0].keys()))
bodies = sorted({r['body'] for r in rows})
print('Body types:', bodies)
ranges = [int(r['range_km']) for r in rows if r['range_km'].isdigit()]
print('Range km min/max/avg:', min(ranges), max(ranges), sum(ranges)//len(ranges))
budget = [int(r['price_from']) for r in rows if r['price_from'].isdigit()]
print('Price 45-75k:', sum(1 for p in budget if 45000<=p<=75000), 'of', len(budget))
print('Missing expected metrics: AWD_flag, heat_pump, warranty_years, model_year, WLTP_verified')
