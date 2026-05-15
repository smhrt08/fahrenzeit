#!/usr/bin/env python3
"""
fetch_cars.py
=============
Fetches all passenger vehicle makes & models from the free NHTSA vPIC API
for model years 2018–present, then merges in pricing data from cars_pricing.json
(manually maintained KBB fair purchase prices + original MSRP estimates).

Output: data/cars.json

Run this whenever you want to refresh the car list or update pricing:
    python3 scripts/fetch_cars.py

Dependencies: none (uses only Python stdlib)
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

START_YEAR = 2018
END_YEAR = datetime.now().year  # auto-increments each January
NHTSA_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles"

# Well-known mainstream makes to include (filters out obscure/commercial brands)
# Add or remove makes here to control scope
INCLUDED_MAKES = {
    "Acura", "Alfa Romeo", "Audi", "BMW", "Buick", "Cadillac", "Chevrolet",
    "Chrysler", "Dodge", "Ferrari", "Fiat", "Ford", "Genesis", "GMC",
    "Honda", "Hyundai", "Infiniti", "Jaguar", "Jeep", "Kia", "Lamborghini",
    "Land Rover", "Lexus", "Lincoln", "Maserati", "Mazda", "Mercedes-Benz",
    "MINI", "Mitsubishi", "Nissan", "Porsche", "Ram", "Rivian", "Rolls-Royce",
    "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo",
}

# Body type mappings: model name keywords → body type
# Used to auto-classify when NHTSA doesn't provide body type
BODY_TYPE_HINTS = {
    # SUVs / Crossovers
    "RAV4": "SUV", "CR-V": "SUV", "Escape": "SUV", "Equinox": "SUV",
    "Rogue": "SUV", "Tucson": "SUV", "Sportage": "SUV", "Forester": "SUV",
    "Outback": "SUV", "Compass": "SUV", "Cherokee": "SUV", "Grand Cherokee": "SUV",
    "Explorer": "SUV", "Edge": "SUV", "Traverse": "SUV", "Pilot": "SUV",
    "Highlander": "SUV", "Pathfinder": "SUV", "4Runner": "SUV", "Sequoia": "SUV",
    "Expedition": "SUV", "Suburban": "SUV", "Tahoe": "SUV", "Yukon": "SUV",
    "Escalade": "SUV", "Navigator": "SUV", "Armada": "SUV", "Land Cruiser": "SUV",
    "Model X": "SUV", "Model Y": "SUV", "EV6": "SUV", "Ioniq 5": "SUV",
    "Ioniq 6": "SUV", "ID.4": "SUV", "Bronco": "SUV", "Bronco Sport": "SUV",
    "Blazer": "SUV", "Trax": "SUV", "Trailblazer": "SUV", "Encore": "SUV",
    "Envision": "SUV", "Enclave": "SUV", "Acadia": "SUV", "Terrain": "SUV",
    "XT4": "SUV", "XT5": "SUV", "XT6": "SUV", "RX": "SUV", "NX": "SUV",
    "UX": "SUV", "GX": "SUV", "LX": "SUV", "QX50": "SUV", "QX60": "SUV",
    "QX80": "SUV", "MDX": "SUV", "RDX": "SUV", "Q3": "SUV", "Q5": "SUV",
    "Q7": "SUV", "Q8": "SUV", "X1": "SUV", "X3": "SUV", "X5": "SUV",
    "X7": "SUV", "GLC": "SUV", "GLE": "SUV", "GLS": "SUV", "GLB": "SUV",
    "GLA": "SUV", "Macan": "SUV", "Cayenne": "SUV", "Urus": "SUV",
    "Defender": "SUV", "Discovery": "SUV", "Range Rover": "SUV",
    "Wrangler": "SUV", "Gladiator": "Truck", "CX-5": "SUV", "CX-9": "SUV",
    "CX-50": "SUV", "CX-90": "SUV", "Santa Fe": "SUV", "Palisade": "SUV",
    "Telluride": "SUV", "Sorento": "SUV", "Carnival": "Minivan",
    "Venue": "SUV", "Kona": "SUV", "Tucson": "SUV",
    "Ascent": "SUV", "Crosstrek": "SUV",
    "GV70": "SUV", "GV80": "SUV", "GV90": "SUV",
    "Stelvio": "SUV",
    # Trucks
    "F-150": "Truck", "F-250": "Truck", "F-350": "Truck",
    "Silverado": "Truck", "Sierra": "Truck", "RAM 1500": "Truck",
    "Ram 1500": "Truck", "Tundra": "Truck", "Tacoma": "Truck",
    "Frontier": "Truck", "Ranger": "Truck", "Colorado": "Truck",
    "Canyon": "Truck", "Titan": "Truck", "Ridgeline": "Truck",
    "R1T": "Truck", "Maverick": "Truck", "Santa Cruz": "Truck",
    # Minivans
    "Odyssey": "Minivan", "Sienna": "Minivan", "Pacifica": "Minivan",
    "Voyager": "Minivan", "Sedona": "Minivan",
    # Sports / Performance
    "Mustang": "Sports Car", "Corvette": "Sports Car", "Camaro": "Sports Car",
    "Challenger": "Sports Car", "Charger": "Sports Car", "86": "Sports Car",
    "BRZ": "Sports Car", "Supra": "Sports Car", "Z": "Sports Car",
    "911": "Sports Car", "718": "Sports Car", "Boxster": "Sports Car",
    "Cayman": "Sports Car", "F-Type": "Sports Car", "Model S": "Sedan",
    "Model 3": "Sedan", "Giulia": "Sedan", "4C": "Sports Car",
    # Sedans / Cars
    "Camry": "Sedan", "Accord": "Sedan", "Civic": "Sedan", "Corolla": "Sedan",
    "Altima": "Sedan", "Sentra": "Sedan", "Malibu": "Sedan", "Impala": "Sedan",
    "Fusion": "Sedan", "Sonata": "Sedan", "Elantra": "Sedan", "Optima": "Sedan",
    "K5": "Sedan", "3 Series": "Sedan", "5 Series": "Sedan", "7 Series": "Sedan",
    "A4": "Sedan", "A6": "Sedan", "A8": "Sedan", "C-Class": "Sedan",
    "E-Class": "Sedan", "S-Class": "Sedan", "IS": "Sedan", "ES": "Sedan",
    "LS": "Sedan", "Q50": "Sedan", "Q60": "Coupe", "G70": "Sedan",
    "G80": "Sedan", "G90": "Sedan", "Mazda3": "Sedan", "Mazda6": "Sedan",
    "Impreza": "Sedan", "Legacy": "Sedan", "Jetta": "Sedan", "Passat": "Sedan",
    "Arteon": "Sedan", "S60": "Sedan", "S90": "Sedan",
    "Ghibli": "Sedan", "Quattroporte": "Sedan",
    "CT5": "Sedan", "CT4": "Sedan", "Regal": "Sedan",
    "300": "Sedan", "200": "Sedan",
    "Ioniq": "Sedan", "Prius": "Sedan", "Insight": "Sedan",
    "Niro": "Sedan",
    # Hatchbacks
    "Golf": "Hatchback", "Mazda3": "Hatchback", "Fit": "Hatchback",
    "Yaris": "Hatchback", "Fiesta": "Hatchback", "Focus": "Hatchback",
    "Veloster": "Hatchback", "i3": "Hatchback",
    # Wagons
    "V60": "Wagon", "V90": "Wagon", "Outback": "Wagon", "6 Series GT": "Wagon",
    "A4 Allroad": "Wagon", "A6 Allroad": "Wagon",
    # Convertibles
    "Miata": "Convertible", "MX-5": "Convertible",
    "Boxster": "Convertible", "911 Cabriolet": "Convertible",
    "4 Series Convertible": "Convertible",
}

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "cars.json"
PRICING_PATH = Path(__file__).parent.parent / "data" / "cars_pricing.json"


def nhtsa_get(path):
    """Make a GET request to the NHTSA vPIC API."""
    url = f"{NHTSA_BASE}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "car-ranking-project/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"  ⚠ Network error for {path}: {e}")
        return None
    except Exception as e:
        print(f"  ⚠ Error for {path}: {e}")
        return None


def get_all_makes():
    """Fetch all makes for passenger cars from NHTSA."""
    print("Fetching all vehicle makes from NHTSA...")
    data = nhtsa_get("GetMakesForVehicleType/car?format=json")
    if not data:
        return []
    makes = [m["MakeName"].strip().title() for m in data.get("Results", [])]
    # Filter to well-known consumer brands
    makes = [m for m in makes if m in INCLUDED_MAKES]
    print(f"  → {len(makes)} makes after filtering")
    return sorted(makes)


def get_models_for_make_year(make, year):
    """Fetch models for a specific make and year."""
    encoded_make = urllib.parse.quote(make) if hasattr(urllib, 'parse') else make.replace(" ", "%20")
    data = nhtsa_get(f"GetModelsForMakeYear/make/{encoded_make}/modelyear/{year}?format=json")
    if not data:
        return []
    return [r["Model_Name"].strip() for r in data.get("Results", [])]


def guess_body_type(model_name):
    """Guess body type from model name using keyword hints."""
    for keyword, body_type in BODY_TYPE_HINTS.items():
        if keyword.lower() in model_name.lower():
            return body_type
    return "Unknown"


def load_pricing():
    """Load existing pricing data if available."""
    if PRICING_PATH.exists():
        with open(PRICING_PATH) as f:
            return json.load(f)
    return {}


def build_pricing_key(year, make, model):
    return f"{year}|{make}|{model}"


def fetch_and_build():
    import urllib.parse  # ensure available

    pricing = load_pricing()
    cars = []
    seen = set()

    makes = get_all_makes()
    if not makes:
        print("ERROR: Could not fetch makes from NHTSA. Check your internet connection.")
        print("Using bundled fallback list instead...")
        makes = sorted(INCLUDED_MAKES)

    total_years = END_YEAR - START_YEAR + 1
    print(f"\nFetching models for {len(makes)} makes × {total_years} years ({START_YEAR}–{END_YEAR})...\n")

    for make in makes:
        print(f"  {make}:")
        for year in range(START_YEAR, END_YEAR + 1):
            models = get_models_for_make_year(make, year)
            for model in models:
                key = f"{year}|{make}|{model}"
                if key in seen:
                    continue
                seen.add(key)

                pricing_key = build_pricing_key(year, make, model)
                pricing_data = pricing.get(pricing_key, {})

                car = {
                    "year": year,
                    "make": make,
                    "model": model,
                    "body_type": pricing_data.get("body_type") or guess_body_type(model),
                    "msrp_original": pricing_data.get("msrp_original", None),
                    "kbb_fair_purchase_price": pricing_data.get("kbb_fair_purchase_price", None),
                    "kbb_last_updated": pricing_data.get("kbb_last_updated", None),
                    "photo_url": pricing_data.get("photo_url", None),
                    "notes": pricing_data.get("notes", ""),
                }
                cars.append(car)

            time.sleep(0.05)  # be polite to NHTSA

        print(f"    → {sum(1 for c in cars if c['make'] == make)} entries so far")

    # Sort: year desc, then make, then model
    cars.sort(key=lambda c: (-c["year"], c["make"], c["model"]))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump({
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "year_range": [START_YEAR, END_YEAR],
                "total_vehicles": len(cars),
                "source": "NHTSA vPIC API + manual KBB pricing",
                "kbb_value_type": "Fair Purchase Price (dealer)",
            },
            "vehicles": cars
        }, f, indent=2)

    print(f"\n✅ Done! {len(cars)} vehicles written to {OUTPUT_PATH}")
    print(f"   {sum(1 for c in cars if c['kbb_fair_purchase_price'])} have KBB pricing data")
    print(f"   {sum(1 for c in cars if not c['kbb_fair_purchase_price'])} need pricing filled in")
    print(f"\nNext step: populate pricing in data/cars_pricing.json (see scripts/update_pricing.py)")


if __name__ == "__main__":
    import urllib.parse
    fetch_and_build()
