#!/usr/bin/env python3
"""
update_pricing.py
=================
Helper script for maintaining KBB fair purchase prices and original MSRPs.

Since KBB values change over time and their official API requires a paid B2B
license, this script provides a structured workflow for manually updating prices.

WORKFLOW:
  1. Run this script to see which vehicles are missing pricing data
  2. Visit https://www.kbb.com/car-values/ and look up each vehicle
  3. Enter the Fair Purchase Price (dealer price) for each
  4. Re-run fetch_cars.py to merge pricing into the main cars.json

Run:
    python3 scripts/update_pricing.py              # show missing prices
    python3 scripts/update_pricing.py --add        # interactive add mode
    python3 scripts/update_pricing.py --import CSV # bulk import from CSV

CSV format for --import:
    year,make,model,body_type,msrp_original,kbb_fair_purchase_price,notes
    2024,Toyota,Camry,Sedan,27000,26500,
    2024,Honda,CR-V,SUV,31000,30200,
"""

import json
import csv
import sys
import argparse
from pathlib import Path
from datetime import date

PRICING_PATH = Path(__file__).parent.parent / "data" / "cars_pricing.json"
CARS_PATH = Path(__file__).parent.parent / "data" / "cars.json"


def load_pricing():
    if PRICING_PATH.exists():
        with open(PRICING_PATH) as f:
            return json.load(f)
    return {}


def save_pricing(pricing):
    PRICING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PRICING_PATH, "w") as f:
        json.dump(pricing, f, indent=2, sort_keys=True)
    print(f"✅ Saved {len(pricing)} pricing records to {PRICING_PATH}")


def load_cars():
    if not CARS_PATH.exists():
        print("cars.json not found. Run fetch_cars.py first.")
        return []
    with open(CARS_PATH) as f:
        data = json.load(f)
    return data.get("vehicles", [])


def make_key(year, make, model):
    return f"{year}|{make}|{model}"


def show_missing(cars, pricing):
    missing = [c for c in cars if not pricing.get(make_key(c["year"], c["make"], c["model"]), {}).get("kbb_fair_purchase_price")]
    print(f"\n{'─'*60}")
    print(f"  {len(missing)} vehicles missing KBB pricing  ({len(cars) - len(missing)} complete)")
    print(f"{'─'*60}")

    # Group by make for readability
    by_make = {}
    for c in missing:
        by_make.setdefault(c["make"], []).append(c)

    for make, vehicles in sorted(by_make.items()):
        years = sorted(set(v["year"] for v in vehicles))
        models = sorted(set(v["model"] for v in vehicles))
        print(f"  {make}: {len(vehicles)} missing  (years: {years[0]}–{years[-1]}, {len(models)} models)")

    print(f"\nKBB lookup: https://www.kbb.com/car-values/")
    print(f"CSV template saved to: data/pricing_template.csv\n")

    # Write a CSV template for easy bulk entry
    template_path = CARS_PATH.parent / "pricing_template.csv"
    with open(template_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "make", "model", "body_type", "msrp_original", "kbb_fair_purchase_price", "notes"])
        w.writeheader()
        for c in sorted(missing, key=lambda x: (x["make"], x["model"], x["year"])):
            w.writerow({
                "year": c["year"],
                "make": c["make"],
                "model": c["model"],
                "body_type": c.get("body_type", ""),
                "msrp_original": "",
                "kbb_fair_purchase_price": "",
                "notes": "",
            })


def interactive_add(pricing):
    print("\nInteractive pricing entry mode")
    print("Enter values for each vehicle. Press Ctrl+C to stop.\n")
    today = date.today().isoformat()

    try:
        while True:
            year = input("Year (e.g. 2024): ").strip()
            make = input("Make (e.g. Toyota): ").strip().title()
            model = input("Model (e.g. Camry): ").strip()
            body_type = input("Body type (Sedan/SUV/Truck/Minivan/Sports Car/Hatchback/Wagon/Convertible): ").strip()
            msrp = input("Original MSRP (base price new, e.g. 27000): ").strip()
            kbb = input("KBB Fair Purchase Price (e.g. 26500): ").strip()
            notes = input("Notes (optional): ").strip()

            key = make_key(year, make, model)
            pricing[key] = {
                "year": int(year),
                "make": make,
                "model": model,
                "body_type": body_type,
                "msrp_original": int(msrp) if msrp else None,
                "kbb_fair_purchase_price": int(kbb) if kbb else None,
                "kbb_last_updated": today,
                "notes": notes,
            }
            print(f"  ✓ Saved {year} {make} {model}\n")
    except KeyboardInterrupt:
        print("\n\nStopped.")
    return pricing


def import_csv(csv_path, pricing):
    today = date.today().isoformat()
    added = 0
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("kbb_fair_purchase_price"):
                continue  # skip blank rows
            key = make_key(row["year"], row["make"], row["model"])
            pricing[key] = {
                "year": int(row["year"]),
                "make": row["make"],
                "model": row["model"],
                "body_type": row.get("body_type", ""),
                "msrp_original": int(row["msrp_original"]) if row.get("msrp_original") else None,
                "kbb_fair_purchase_price": int(row["kbb_fair_purchase_price"]),
                "kbb_last_updated": today,
                "notes": row.get("notes", ""),
            }
            added += 1
    print(f"✅ Imported {added} records from {csv_path}")
    return pricing


def main():
    parser = argparse.ArgumentParser(description="Update KBB pricing data")
    parser.add_argument("--add", action="store_true", help="Interactive add mode")
    parser.add_argument("--import", dest="csv_file", metavar="CSV", help="Import from CSV file")
    args = parser.parse_args()

    pricing = load_pricing()
    cars = load_cars()

    if args.csv_file:
        pricing = import_csv(args.csv_file, pricing)
        save_pricing(pricing)
    elif args.add:
        pricing = interactive_add(pricing)
        save_pricing(pricing)
    else:
        show_missing(cars, pricing)
        print("Run with --add to enter prices interactively")
        print("Run with --import pricing_template.csv (after filling it in) to bulk import\n")


if __name__ == "__main__":
    main()
