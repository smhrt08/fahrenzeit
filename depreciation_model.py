#!/usr/bin/env python3
"""
depreciation_model.py
=====================
Estimates current fair market dealer retail value for any car year/make/model
using a brand/model calibrated two-phase depreciation model.

DATA SOURCES (5-year retention calibration):
  iSeeCars 2024-2026, CARFAX, KBB, SlashGear depreciation research

METHODOLOGY:
  1. Mid-trim average transaction price (not base MSRP) as anchor
  2. Two-phase exponential decay:
     Phase 1 (0-5yr): calibrated to match real 5yr retention rates
     Phase 2 (5+yr): slower decay at 40% of phase 1 rate
  3. Floor prevents collapse for extreme depreciators
  4. Brand-level defaults with model-specific overrides

Run:
    python3 scripts/depreciation_model.py --test
    python3 scripts/depreciation_model.py --run
    python3 scripts/depreciation_model.py --make Toyota
"""

import json, math, argparse
from pathlib import Path
from datetime import datetime

CURRENT_YEAR = 2026

BASE_PRICES = {
    "Acura|ILX": 32000, "Acura|Integra": 36000, "Acura|TLX": 46000,
    "Acura|RDX": 48000, "Acura|MDX": 58000, "Acura|NSX": 175000,
    "Acura|ZDX": 68000,
    "Alfa Romeo|Giulia": 52000, "Alfa Romeo|Stelvio": 54000,
    "Alfa Romeo|4C": 65000, "Alfa Romeo|Tonale": 48000, "Alfa Romeo|Junior": 40000,
    "Audi|A3": 38000, "Audi|A4": 46000, "Audi|A5": 52000,
    "Audi|A6": 62000, "Audi|A7": 76000, "Audi|A8": 96000,
    "Audi|Q3": 42000, "Audi|Q4 e-tron": 52000, "Audi|Q5": 52000,
    "Audi|Q7": 64000, "Audi|Q8": 78000, "Audi|Q8 e-tron": 82000,
    "Audi|e-tron": 72000, "Audi|e-tron GT": 112000,
    "Audi|RS3": 66000, "Audi|RS5": 84000, "Audi|RS6": 128000,
    "Audi|RS7": 128000, "Audi|R8": 168000, "Audi|TT": 52000,
    "Audi|S3": 54000, "Audi|S4": 60000, "Audi|S5": 66000,
    "Audi|SQ5": 64000, "Audi|SQ7": 80000, "Audi|SQ8": 98000,
    "BMW|2 Series": 42000, "BMW|3 Series": 50000, "BMW|4 Series": 56000,
    "BMW|5 Series": 66000, "BMW|7 Series": 108000, "BMW|8 Series": 98000,
    "BMW|X1": 44000, "BMW|X2": 46000, "BMW|X3": 54000,
    "BMW|X4": 62000, "BMW|X5": 74000, "BMW|X6": 78000,
    "BMW|X7": 92000, "BMW|i3": 46000, "BMW|i4": 74000,
    "BMW|i5": 76000, "BMW|i7": 118000, "BMW|iX": 96000,
    "BMW|iX1": 44000, "BMW|iX3": 62000,
    "BMW|M2": 74000, "BMW|M3": 86000, "BMW|M4": 88000,
    "BMW|M5": 124000, "BMW|M8": 148000, "BMW|Z4": 62000,
    "Buick|Encore": 27000, "Buick|Encore GX": 30000, "Buick|Envision": 38000,
    "Buick|Enclave": 52000, "Buick|Envista": 28000, "Buick|Electra E4": 50000,
    "Cadillac|CT4": 40000, "Cadillac|CT5": 46000, "Cadillac|XT4": 44000,
    "Cadillac|XT5": 52000, "Cadillac|XT6": 58000, "Cadillac|Escalade": 92000,
    "Cadillac|Escalade ESV": 98000, "Cadillac|LYRIQ": 66000,
    "Cadillac|CELESTIQ": 350000, "Cadillac|OPTIQ": 62000, "Cadillac|VISTIQ": 86000,
    "Chevrolet|Malibu": 27000, "Chevrolet|Camaro": 36000, "Chevrolet|Corvette": 78000,
    "Chevrolet|Equinox": 34000, "Chevrolet|Equinox EV": 42000, "Chevrolet|Trax": 25000,
    "Chevrolet|Trailblazer": 28000, "Chevrolet|Blazer": 40000, "Chevrolet|Blazer EV": 52000,
    "Chevrolet|Traverse": 44000, "Chevrolet|Tahoe": 62000, "Chevrolet|Suburban": 68000,
    "Chevrolet|Colorado": 38000, "Chevrolet|Silverado 1500": 54000,
    "Chevrolet|Silverado EV": 50000, "Chevrolet|Bolt EV": 30000,
    "Chevrolet|Bolt EUV": 32000, "Chevrolet|Spark": 16000,
    "Chevrolet|Encore": 26000, "Chevrolet|Encore GX": 28000,
    "Chrysler|300": 34000, "Chrysler|Pacifica": 44000, "Chrysler|Voyager": 32000,
    "Chrysler|Airflow": 55000,
    "Dodge|Challenger": 42000, "Dodge|Charger": 44000, "Dodge|Durango": 46000,
    "Dodge|Hornet": 36000,
    "Ferrari|488": 280000, "Ferrari|F8": 300000, "Ferrari|Roma": 245000,
    "Ferrari|Portofino": 240000, "Ferrari|GTC4Lusso": 320000,
    "Ferrari|SF90 Stradale": 540000, "Ferrari|296 GTB": 345000,
    "Ferrari|Purosangue": 425000, "Ferrari|12Cilindri": 440000,
    "Fiat|500": 18000, "Fiat|500X": 26000, "Fiat|500L": 24000,
    "Fiat|500e": 36000, "Fiat|Panda": 24000,
    "Ford|Mustang": 38000, "Ford|Mustang Mach-E": 52000, "Ford|F-150": 58000,
    "Ford|F-150 Lightning": 68000, "Ford|Ranger": 40000, "Ford|Maverick": 30000,
    "Ford|Explorer": 46000, "Ford|Escape": 34000, "Ford|Edge": 40000,
    "Ford|Expedition": 66000, "Ford|Bronco": 46000, "Ford|Bronco Sport": 36000,
    "Ford|EcoSport": 24000, "Ford|Fusion": 28000,
    "Genesis|G70": 42000, "Genesis|G80": 56000, "Genesis|G90": 96000,
    "Genesis|GV70": 50000, "Genesis|GV80": 60000, "Genesis|GV60": 54000,
    "Genesis|G80 Electric": 88000, "Genesis|GV70 Electrified": 74000,
    "Genesis|GV90": 108000,
    "GMC|Terrain": 36000, "GMC|Acadia": 46000, "GMC|Yukon": 66000,
    "GMC|Yukon XL": 70000, "GMC|Sierra 1500": 54000, "GMC|Sierra EV": 60000,
    "GMC|Canyon": 42000, "GMC|Envoy": 44000, "GMC|Hummer EV": 92000,
    "GMC|Hummer EV SUV": 92000,
    "Honda|Accord": 34000, "Honda|Civic": 27000, "Honda|Insight": 26000,
    "Honda|CR-V": 36000, "Honda|CR-V Hybrid": 40000, "Honda|HR-V": 28000,
    "Honda|Passport": 44000, "Honda|Pilot": 50000, "Honda|Ridgeline": 46000,
    "Honda|Odyssey": 44000, "Honda|Fit": 20000, "Honda|Prologue": 54000,
    "Hyundai|Elantra": 25000, "Hyundai|Sonata": 30000, "Hyundai|Tucson": 32000,
    "Hyundai|Santa Fe": 36000, "Hyundai|Palisade": 44000, "Hyundai|Venue": 23000,
    "Hyundai|Kona": 28000, "Hyundai|Kona Electric": 40000, "Hyundai|Ioniq": 26000,
    "Hyundai|Ioniq 5": 48000, "Hyundai|Ioniq 6": 44000, "Hyundai|Ioniq 9": 68000,
    "Hyundai|Nexo": 64000, "Hyundai|Accent": 19000, "Hyundai|Veloster": 24000,
    "Hyundai|Santa Cruz": 32000,
    "Infiniti|Q50": 44000, "Infiniti|Q60": 50000, "Infiniti|QX50": 46000,
    "Infiniti|QX55": 54000, "Infiniti|QX60": 56000, "Infiniti|QX80": 82000,
    "Jaguar|XE": 40000, "Jaguar|XF": 52000, "Jaguar|F-Type": 72000,
    "Jaguar|E-Pace": 48000, "Jaguar|F-Pace": 58000, "Jaguar|I-Pace": 78000,
    "Jaguar|Type 00": 130000,
    "Jeep|Wrangler": 42000, "Jeep|Wrangler 4xe": 60000, "Jeep|Grand Cherokee": 50000,
    "Jeep|Grand Cherokee 4xe": 68000, "Jeep|Cherokee": 34000, "Jeep|Compass": 32000,
    "Jeep|Renegade": 28000, "Jeep|Gladiator": 48000, "Jeep|Grand Wagoneer": 100000,
    "Jeep|Wagoneer": 68000, "Jeep|Avenger": 28000, "Jeep|Recon": 58000,
    "Kia|Forte": 23000, "Kia|K5": 30000, "Kia|Optima": 28000,
    "Kia|Stinger": 42000, "Kia|Niro": 32000, "Kia|Niro EV": 46000,
    "Kia|Sportage": 34000, "Kia|Sorento": 38000, "Kia|Telluride": 46000,
    "Kia|Soul": 25000, "Kia|Seltos": 28000, "Kia|EV6": 50000,
    "Kia|EV9": 64000, "Kia|Carnival": 40000, "Kia|Sedona": 36000,
    "Kia|Rio": 19000, "Kia|Cadenza": 38000,
    "Lamborghini|Huracan": 240000, "Lamborghini|Urus": 260000,
    "Lamborghini|Revuelto": 560000, "Lamborghini|Temerario": 280000,
    "Land Rover|Discovery": 64000, "Land Rover|Discovery Sport": 52000,
    "Land Rover|Range Rover Sport": 84000, "Land Rover|Range Rover Velar": 68000,
    "Land Rover|Range Rover Evoque": 54000, "Land Rover|Range Rover": 120000,
    "Land Rover|Defender": 66000,
    "Lexus|IS": 46000, "Lexus|ES": 48000, "Lexus|LS": 86000,
    "Lexus|UX": 40000, "Lexus|NX": 46000, "Lexus|RX": 56000,
    "Lexus|GX": 76000, "Lexus|GX 550": 76000, "Lexus|LX": 98000,
    "Lexus|LC": 102000, "Lexus|RC": 50000, "Lexus|RZ": 62000, "Lexus|TX": 62000,
    "Lincoln|MKZ": 42000, "Lincoln|Continental": 52000, "Lincoln|Corsair": 44000,
    "Lincoln|Nautilus": 52000, "Lincoln|Aviator": 62000, "Lincoln|Navigator": 92000,
    "MINI|Hardtop": 28000, "MINI|Convertible": 32000, "MINI|Clubman": 34000,
    "MINI|Countryman": 36000, "MINI|Cooper SE": 34000, "MINI|Aceman": 40000,
    "MINI|John Cooper Works": 40000,
    "Maserati|Ghibli": 84000, "Maserati|Quattroporte": 118000,
    "Maserati|Levante": 84000, "Maserati|Grecale": 72000,
    "Maserati|GranTurismo": 200000, "Maserati|MC20": 240000,
    "Mazda|Mazda3": 27000, "Mazda|Mazda6": 28000, "Mazda|CX-3": 24000,
    "Mazda|CX-30": 28000, "Mazda|CX-5": 34000, "Mazda|CX-50": 36000,
    "Mazda|CX-9": 42000, "Mazda|CX-90": 50000, "Mazda|MX-5 Miata": 32000,
    "Mazda|MX-30": 38000,
    "Mercedes-Benz|A-Class": 38000, "Mercedes-Benz|C-Class": 52000,
    "Mercedes-Benz|E-Class": 66000, "Mercedes-Benz|S-Class": 128000,
    "Mercedes-Benz|CLA": 46000, "Mercedes-Benz|CLS": 80000,
    "Mercedes-Benz|GLA": 46000, "Mercedes-Benz|GLB": 48000,
    "Mercedes-Benz|GLC": 56000, "Mercedes-Benz|GLE": 68000,
    "Mercedes-Benz|GLS": 104000, "Mercedes-Benz|G-Class": 156000,
    "Mercedes-Benz|EQB": 62000, "Mercedes-Benz|EQE": 84000,
    "Mercedes-Benz|EQE SUV": 88000, "Mercedes-Benz|EQS": 116000,
    "Mercedes-Benz|EQS SUV": 118000, "Mercedes-Benz|AMG GT": 134000,
    "Mercedes-Benz|SL": 106000, "Mercedes-Benz|Sprinter": 50000,
    "Mitsubishi|Outlander": 32000, "Mitsubishi|Outlander PHEV": 44000,
    "Mitsubishi|Eclipse Cross": 30000, "Mitsubishi|Mirage": 18000,
    "Mitsubishi|Outlander Sport": 28000,
    "Nissan|Altima": 30000, "Nissan|Sentra": 24000, "Nissan|Maxima": 40000,
    "Nissan|Versa": 19000, "Nissan|Rogue": 34000, "Nissan|Rogue Sport": 28000,
    "Nissan|Murano": 40000, "Nissan|Pathfinder": 42000, "Nissan|Armada": 60000,
    "Nissan|Kicks": 25000, "Nissan|Frontier": 36000, "Nissan|Titan": 46000,
    "Nissan|Leaf": 32000, "Nissan|Ariya": 50000, "Nissan|Z": 46000,
    "Nissan|370Z": 36000,
    "Porsche|Macan": 66000, "Porsche|Macan Electric": 84000,
    "Porsche|Cayenne": 84000, "Porsche|Cayenne Coupe": 90000,
    "Porsche|Taycan": 96000, "Porsche|Taycan Cross Turismo": 100000,
    "Porsche|Taycan Sport Turismo": 100000, "Porsche|911": 128000,
    "Porsche|718 Cayman": 74000, "Porsche|718 Boxster": 76000,
    "Porsche|Panamera": 104000,
    "Ram|1500": 52000, "Ram|1500 REV": 68000,
    "Rivian|R1T": 76000, "Rivian|R1S": 80000, "Rivian|R2": 52000,
    "Rolls-Royce|Ghost": 360000, "Rolls-Royce|Phantom": 490000,
    "Rolls-Royce|Wraith": 360000, "Rolls-Royce|Dawn": 390000,
    "Rolls-Royce|Cullinan": 370000, "Rolls-Royce|Spectre": 460000,
    "Rolls-Royce|Black Badge Ghost": 420000,
    "Subaru|Impreza": 24000, "Subaru|Legacy": 28000, "Subaru|Outback": 34000,
    "Subaru|Forester": 30000, "Subaru|Crosstrek": 28000, "Subaru|Ascent": 42000,
    "Subaru|BRZ": 34000, "Subaru|WRX": 34000, "Subaru|Solterra": 50000,
    "Tesla|Model 3": 46000, "Tesla|Model S": 84000, "Tesla|Model X": 90000,
    "Tesla|Model Y": 50000, "Tesla|Cybertruck": 72000, "Tesla|Roadster": 220000,
    "Toyota|Camry": 32000, "Toyota|Corolla": 26000, "Toyota|Avalon": 44000,
    "Toyota|Prius": 34000, "Toyota|RAV4": 34000, "Toyota|RAV4 Hybrid": 38000,
    "Toyota|RAV4 Prime": 46000, "Toyota|Highlander": 46000, "Toyota|4Runner": 46000,
    "Toyota|Sequoia": 72000, "Toyota|Land Cruiser": 66000, "Toyota|Venza": 40000,
    "Toyota|Crown": 48000, "Toyota|bZ4X": 50000, "Toyota|Tacoma": 44000,
    "Toyota|Tundra": 54000, "Toyota|Sienna": 44000, "Toyota|86": 32000,
    "Toyota|GR86": 34000, "Toyota|Supra": 52000, "Toyota|C-HR": 26000,
    "Toyota|Corolla Cross": 28000,
    "Volkswagen|Jetta": 26000, "Volkswagen|Passat": 30000, "Volkswagen|Arteon": 44000,
    "Volkswagen|Golf": 28000, "Volkswagen|Golf GTI": 38000, "Volkswagen|Golf R": 52000,
    "Volkswagen|Tiguan": 34000, "Volkswagen|Atlas": 44000,
    "Volkswagen|Atlas Cross Sport": 44000, "Volkswagen|ID.4": 48000,
    "Volkswagen|ID.Buzz": 66000, "Volkswagen|Taos": 30000,
    "Volvo|S60": 46000, "Volvo|S90": 62000, "Volvo|V60": 52000,
    "Volvo|V90": 66000, "Volvo|XC40": 44000, "Volvo|XC40 Recharge": 62000,
    "Volvo|XC60": 52000, "Volvo|XC90": 66000, "Volvo|EX30": 42000,
    "Volvo|EX90": 86000, "Volvo|C40 Recharge": 62000,
}

BRAND_5YR_RETENTION = {
    "Porsche": 0.72, "Toyota": 0.62, "Honda": 0.60, "Subaru": 0.58,
    "Jeep": 0.57, "Ford": 0.55, "Ram": 0.57, "GMC": 0.54,
    "Chevrolet": 0.54, "Mazda": 0.53, "Nissan": 0.48, "Hyundai": 0.48,
    "Kia": 0.48, "Volkswagen": 0.47, "Mitsubishi": 0.44,
    "Acura": 0.50, "Genesis": 0.52, "Lexus": 0.58, "MINI": 0.45,
    "Buick": 0.43, "Audi": 0.38, "BMW": 0.35, "Cadillac": 0.42,
    "Infiniti": 0.32, "Lincoln": 0.36, "Volvo": 0.35,
    "Mercedes-Benz": 0.35, "Alfa Romeo": 0.38, "Rivian": 0.55,
    "Tesla": 0.45, "Land Rover": 0.22, "Jaguar": 0.28,
    "Maserati": 0.22, "Chrysler": 0.42, "Dodge": 0.46, "Fiat": 0.40,
    "Lamborghini": 0.60, "Ferrari": 0.75, "Rolls-Royce": 0.55,
}

MODEL_5YR_OVERRIDE = {
    "Toyota|4Runner": 0.72, "Toyota|Tacoma": 0.68, "Toyota|Land Cruiser": 0.78,
    "Toyota|GR86": 0.62, "Toyota|Supra": 0.68, "Toyota|RAV4 Hybrid": 0.64,
    "Toyota|RAV4 Prime": 0.61, "Toyota|Prius": 0.60,
    "Honda|Ridgeline": 0.58,
    "Porsche|911": 0.91, "Porsche|718 Cayman": 0.72, "Porsche|718 Boxster": 0.70,
    "Porsche|Macan": 0.58, "Porsche|Cayenne": 0.55,
    "Porsche|Taycan": 0.50, "Porsche|Taycan Cross Turismo": 0.50,
    "Porsche|Taycan Sport Turismo": 0.50,
    "Jeep|Wrangler": 0.70, "Jeep|Wrangler 4xe": 0.55, "Jeep|Gladiator": 0.65,
    "Jeep|Grand Wagoneer": 0.45,
    "Ford|F-150": 0.60, "Ford|Bronco": 0.65, "Ford|Mustang": 0.58,
    "Ford|F-150 Lightning": 0.45, "Ford|Mustang Mach-E": 0.40,
    "Chevrolet|Corvette": 0.76, "Chevrolet|Colorado": 0.58,
    "Chevrolet|Silverado 1500": 0.58, "Chevrolet|Camaro": 0.50,
    "Chevrolet|Bolt EV": 0.30, "Chevrolet|Equinox EV": 0.40,
    "GMC|Sierra 1500": 0.57, "GMC|Canyon": 0.57, "GMC|Hummer EV": 0.52,
    "Tesla|Model 3": 0.52, "Tesla|Model Y": 0.50,
    "Tesla|Model S": 0.38, "Tesla|Model X": 0.38, "Tesla|Cybertruck": 0.48,
    "Land Rover|Defender": 0.52, "Land Rover|Range Rover": 0.14,
    "Land Rover|Range Rover Sport": 0.30, "Land Rover|Discovery": 0.25,
    "Jaguar|F-Type": 0.38, "Jaguar|I-Pace": 0.22,
    "Maserati|Grecale": 0.22, "Maserati|Ghibli": 0.28, "Maserati|MC20": 0.60,
    "BMW|M2": 0.56, "BMW|M3": 0.62, "BMW|M4": 0.58,
    "BMW|7 Series": 0.27, "BMW|5 Series": 0.30, "BMW|X3": 0.34, "BMW|i3": 0.25,
    "Nissan|Z": 0.60, "Nissan|Leaf": 0.25,
    "Infiniti|QX80": 0.20, "Infiniti|QX50": 0.35,
    "Kia|Telluride": 0.65, "Kia|EV6": 0.48,
    "Mercedes-Benz|S-Class": 0.33, "Mercedes-Benz|G-Class": 0.68,
    "Mercedes-Benz|EQS": 0.28, "Mercedes-Benz|EQS SUV": 0.28,
    "Mercedes-Benz|EQE": 0.32,
    "Subaru|WRX": 0.60, "Subaru|BRZ": 0.60, "Subaru|Outback": 0.58,
    "Lamborghini|Huracan": 0.55, "Lamborghini|Urus": 0.50,
    "Lamborghini|Revuelto": 0.78,
    "Ferrari|488": 0.85, "Ferrari|F8": 0.80, "Ferrari|SF90 Stradale": 0.88,
    "Ferrari|296 GTB": 0.78, "Ferrari|Roma": 0.75, "Ferrari|Portofino": 0.72,
    "Ferrari|Purosangue": 0.82, "Ferrari|12Cilindri": 0.90,
    "Rolls-Royce|Ghost": 0.52, "Rolls-Royce|Phantom": 0.60,
    "Rolls-Royce|Cullinan": 0.58, "Rolls-Royce|Spectre": 0.65,
    "Volvo|XC40 Recharge": 0.30, "Volvo|C40 Recharge": 0.30,
    "Dodge|Challenger": 0.52, "Dodge|Charger": 0.46,
    "Acura|NSX": 0.80,
    "Hyundai|Ioniq 5": 0.46, "Hyundai|Kona Electric": 0.42,
    "Volkswagen|ID.4": 0.40,
    "Ram|1500": 0.62,
    "Rivian|R1T": 0.60, "Rivian|R1S": 0.60,
}


def retention_at_age(age_years: float, five_yr_retention: float) -> float:
    """Two-phase depreciation curve calibrated to real 5-year retention rates."""
    if age_years <= 0:
        return 0.97

    # Floor is below 5yr retention so the curve has headroom to interpolate
    if five_yr_retention < 0.20:
        floor = five_yr_retention * 0.50
    else:
        floor = max(0.08, five_yr_retention * 0.38)

    ceiling = 0.97
    numerator = five_yr_retention - floor
    denominator = ceiling - floor
    if denominator <= 0 or numerator <= 0:
        return max(floor, five_yr_retention)

    ratio = max(0.001, numerator / denominator)
    k = -math.log(ratio) / 5.0

    if age_years <= 5:
        retention = (ceiling - floor) * math.exp(-k * age_years) + floor
    else:
        # Phase 2: slower decay
        k2 = k * 0.40
        extra = age_years - 5
        retention = (five_yr_retention - floor) * math.exp(-k2 * extra) + floor

    return max(floor, min(ceiling, retention))


def get_five_yr_retention(make: str, model: str) -> float:
    key = f"{make}|{model}"
    if key in MODEL_5YR_OVERRIDE:
        return MODEL_5YR_OVERRIDE[key]
    return BRAND_5YR_RETENTION.get(make, 0.45)


def get_base_price(make: str, model: str) -> int:
    return BASE_PRICES.get(f"{make}|{model}", 38000)


def estimate_value(make: str, model: str, model_year: int) -> dict:
    base_price  = get_base_price(make, model)
    five_yr_ret = get_five_yr_retention(make, model)
    age         = max(0, CURRENT_YEAR - model_year)
    retention   = retention_at_age(age, five_yr_ret)
    est_value   = int(base_price * retention / 500) * 500

    return {
        "make": make, "model": model, "model_year": model_year,
        "base_price_mid_trim": base_price, "age_years": age,
        "five_yr_retention": five_yr_ret,
        "retention_pct": round(retention * 100, 1),
        "estimated_value": est_value,
        "value_label": f"~${est_value:,}",
        "as_of": str(CURRENT_YEAR),
    }


TEST_CASES = [
    ("Porsche",        "911",              2020,  90000, 130000),
    ("Ferrari",        "488",              2018, 180000, 280000),
    ("Lamborghini",    "Huracan",          2018, 110000, 175000),
    ("Rolls-Royce",    "Ghost",            2021, 160000, 240000),
    ("Maserati",       "Grecale",          2023,  12000,  32000),
    ("Land Rover",     "Range Rover",      2018,  12000,  35000),
    ("BMW",            "7 Series",         2019,  22000,  50000),
    ("Audi",           "A6",               2018,  16000,  34000),
    ("Mercedes-Benz",  "S-Class",          2018,  30000,  64000),
    ("Tesla",          "Model S",          2018,  24000,  48000),
    ("Toyota",         "Camry",            2018,  15000,  24000),
    ("Toyota",         "4Runner",          2018,  28000,  46000),
    ("Honda",          "CR-V",             2018,  15000,  26000),
    ("Ford",           "F-150",            2021,  34000,  56000),
    ("Ford",           "Mustang",          2018,  18000,  32000),
    ("Chevrolet",      "Corvette",         2020,  56000,  88000),
    ("Nissan",         "Leaf",             2018,   5000,  13000),
    ("Jeep",           "Wrangler",         2018,  24000,  42000),
    ("Dodge",          "Challenger",       2018,  18000,  32000),
    ("Hyundai",        "Sonata",           2020,  13000,  21000),
    ("Kia",            "Telluride",        2020,  28000,  42000),
    ("Subaru",         "Outback",          2020,  18000,  27000),
    ("Porsche",        "Macan",            2019,  28000,  46000),
    ("BMW",            "M3",               2021,  52000,  76000),
    ("Toyota",         "Tacoma",           2018,  26000,  40000),
    ("Ram",            "1500",             2019,  28000,  46000),
    ("Rivian",         "R1T",              2022,  48000,  68000),
    ("BMW",            "X3",               2019,  16000,  34000),
    ("Infiniti",       "QX80",             2018,  12000,  28000),
    ("Mercedes-Benz",  "G-Class",          2019,  88000, 130000),
]


def run_tests():
    print(f"{'='*70}\nDEPRECIATION MODEL TEST  |  as of {CURRENT_YEAR}\n{'='*70}")
    passed = failed = 0
    for make, model, year, lo, hi in TEST_CASES:
        r   = estimate_value(make, model, year)
        val = r["estimated_value"]
        ok  = lo <= val <= hi
        passed += ok; failed += not ok
        s = "✅" if ok else "❌"
        print(f"{s} {year} {make} {model}")
        print(f"   ${val:,}  expected ${lo:,}–${hi:,}  |  "
              f"age={r['age_years']}yr  ret={r['retention_pct']}%  "
              f"anchor=${r['base_price_mid_trim']:,}")
    print(f"\n{passed}/{len(TEST_CASES)} passed, {failed} failed")
    return failed == 0


def run_full(make_filter=None):
    photo_path = Path(__file__).parent.parent / "data" / "photo_needed.json"
    if not photo_path.exists():
        print(f"ERROR: {photo_path} not found."); return None

    with open(photo_path) as f:
        data = json.load(f)

    photos = data["photos"]
    if make_filter:
        photos = [p for p in photos if p["make"].lower() == make_filter.lower()]

    results = []
    for p in photos:
        r = estimate_value(p["make"], p["model"], p["year"])
        r.update({
            "body_type": p.get("body_type", ""),
            "gen_name": p.get("gen_name", ""),
            "gen_year_range": p.get("gen_year_range", ""),
            "photo_filename": p.get("photo_filename", ""),
        })
        results.append(r)

    out_json = Path(__file__).parent.parent / "data" / "car_values.json"
    with open(out_json, "w") as f:
        json.dump({
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "model": "brand-calibrated two-phase exponential depreciation",
                "current_year": CURRENT_YEAR,
                "price_basis": "mid-trim average transaction price",
                "note": "Estimated fair dealer retail values. Not a substitute for actual appraisal.",
                "sources": "5yr retention from iSeeCars 2024, CARFAX, KBB, SlashGear",
            },
            "vehicles": results
        }, f, indent=2)
    print(f"Saved: {out_json}  ({len(results)} vehicles)")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--run",  action="store_true")
    parser.add_argument("--make", help="Filter to one make")
    args = parser.parse_args()
    if args.test:   run_tests()
    elif args.run:  run_full(args.make)
    else:           run_tests()
