# 🚗 Car Ranking Project

A photo library and interactive ranking tool for cars from 2018–present. Browse and rank vehicles using a smart pairwise comparison test that learns your preferences and surfaces your top picks.

---

## Project Structure

```
car-ranking-repo/
├── data/
│   ├── cars.json              # Master vehicle database (generated)
│   ├── cars_pricing.json      # KBB pricing overrides (manually maintained)
│   └── pricing_template.csv   # Auto-generated CSV for bulk pricing entry
│
├── photos/
│   └── {make}/{year}_{model}.jpg   # Car photos (add manually or via script)
│
├── scripts/
│   ├── fetch_cars.py          # Sync vehicle list from NHTSA API
│   ├── generate_seed_data.py  # Regenerate seed data from curated list
│   └── update_pricing.py      # Add/update KBB pricing data
│
├── index.html                 # ← Interactive ranking test (open this!)
└── README.md
```

---

## Quick Start

### 1. Open the Ranking Test
Just open `index.html` in any browser — no server needed.

```bash
open index.html
# or double-click index.html in Finder/Explorer
```

### 2. Refresh the Vehicle List (Annual Update)
Each year, run this to pull new models from NHTSA's free public API:

```bash
python3 scripts/fetch_cars.py
```

Requirements: Python 3.8+, no external packages needed.

### 3. Update KBB Pricing
KBB fair purchase prices change over time. To update them:

**Option A – Interactive (one vehicle at a time):**
```bash
python3 scripts/update_pricing.py --add
```

**Option B – Bulk via CSV (recommended for large updates):**
```bash
# 1. Generate a template of vehicles missing pricing
python3 scripts/update_pricing.py

# 2. Fill in the generated data/pricing_template.csv
#    (look up values at https://www.kbb.com/car-values/)

# 3. Import the filled CSV
python3 scripts/update_pricing.py --import data/pricing_template.csv

# 4. Regenerate cars.json with updated pricing
python3 scripts/fetch_cars.py
```

---

## Vehicle Database (`data/cars.json`)

The master database covers **2018–present** across **39 makes** and **400+ models**.

### Schema
```json
{
  "meta": {
    "generated_at": "...",
    "total_vehicles": 2696,
    "kbb_value_type": "Fair Purchase Price (dealer)"
  },
  "vehicles": [
    {
      "year": 2024,
      "make": "Toyota",
      "model": "Camry",
      "body_type": "Sedan",
      "msrp_original": 25000,
      "kbb_fair_purchase_price": 28500,
      "kbb_last_updated": "2024-Q4",
      "photo_url": null,
      "notes": ""
    }
  ]
}
```

### Body Types
`Sedan` · `SUV` · `Truck` · `Sports Car` · `Coupe` · `Hatchback` · `Wagon` · `Convertible` · `Minivan`

### Covered Makes (39 total)
Acura, Alfa Romeo, Audi, BMW, Buick, Cadillac, Chevrolet, Chrysler, Dodge, Ferrari, Fiat, Ford, Genesis, GMC, Honda, Hyundai, Infiniti, Jaguar, Jeep, Kia, Lamborghini, Land Rover, Lexus, Lincoln, Maserati, Mazda, Mercedes-Benz, MINI, Mitsubishi, Nissan, Porsche, Ram, Rivian, Rolls-Royce, Subaru, Tesla, Toyota, Volkswagen, Volvo

---

## Adding Photos

Photos live in `photos/{Make}/{Year}_{Model}.jpg`. The naming convention:

```
photos/Toyota/2024_Camry.jpg
photos/Ford/2023_F-150.jpg
photos/BMW/2024_X5.jpg
```

The ranking app will automatically display photos if they exist at this path.

**Tip:** A good free source for car press photos is each manufacturer's media site (e.g., media.toyota.com, media.ford.com).

---

## Ranking Algorithm

The interactive test uses **adaptive pairwise comparison**:

1. **Forced choice** — You're shown two cars, pick the one you prefer
2. **Adaptive elimination** — Cars that consistently lose are deprioritized
3. **Convergence** — As your preferences become clear, the algorithm focuses on your top contenders
4. **Final ranking** — Your top cars are displayed with scores

This is based on a simplified version of the **Bradley-Terry model**, similar to how chess ratings (Elo) work. Each win/loss updates a vehicle's score, and the algorithm prioritizes matchups that give the most information.

---

## Annual Maintenance Checklist

| Task | When | Command |
|------|------|---------|
| Add new model year vehicles | January each year | `python3 scripts/fetch_cars.py` |
| Update KBB fair purchase prices | Quarterly | `python3 scripts/update_pricing.py --import ...` |
| Add new photos | As new models arrive | Copy to `photos/{Make}/` |
| Update `INCLUDED_MAKES` in fetch_cars.py | When new brands launch | Edit the set in the script |

---

## License

MIT — use freely, no attribution required.
