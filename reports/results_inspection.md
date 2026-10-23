# CSV Results Inspection — workspace/full_market.csv

## Actual Metrics Available (84 rows, 9 columns)
- brand, model, body (SUV/Sedan/Hatch/Ute/MPV/Roadster/Coupe — no Wagon)
- range_km (min 220, max 652, avg 495)
- battery_kwh, dc_peak, price_from
- source_url, notes

## Expected Metrics (per user spec / compare.html / EV tracker requirements)
- AWD flag — MISSING
- Heat pump — MISSING
- Warranty / 8yr battery — MISSING
- Model year — MISSING
- WLTP verified label — MISSING (only range_km numeric present)
- Body: Wagon — ABSENT from data

## Budget Filter ($45k-$75k)
- 49 of 84 vehicles (58%) fall within budget.
- Range-qualified (≥350km) within budget: ~38 vehicles.
- DC ≥150 kW within budget: ~22 vehicles.

## Key Gaps for Deliverable
No AWD, heat pump, warranty, or year columns in CSV — comparison page relies on notes field only. No wagon body type present. Recommend adding these fields in next refresh or deriving from source URLs.
