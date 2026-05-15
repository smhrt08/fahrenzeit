#!/usr/bin/env python3
"""
generate_seed_data.py
=====================
Generates a seed cars.json from a curated internal dataset.
This gives the project a working dataset immediately, without needing
to call the NHTSA API. Run fetch_cars.py later to sync with live NHTSA data.

Pricing reflects approximate 2024 KBB Fair Purchase Prices (dealer).
MSRP reflects the base price when the model was new.
"""

import json
from datetime import datetime
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "cars.json"

# Schema per vehicle:
# (year, make, model, body_type, msrp_original, kbb_fair_purchase_price_2024)
# kbb = None means "needs lookup" — run update_pricing.py

VEHICLES = []

# ── TOYOTA ─────────────────────────────────────────────────────────────────
toyota_models = [
    # model, body_type, base_msrp_approx
    ("Camry",        "Sedan",     25000),
    ("Corolla",      "Sedan",     21000),
    ("Avalon",       "Sedan",     36000),  # discontinued 2022
    ("Prius",        "Sedan",     28000),
    ("RAV4",         "SUV",       27000),
    ("RAV4 Hybrid",  "SUV",       31000),
    ("RAV4 Prime",   "SUV",       39000),
    ("Highlander",   "SUV",       36000),
    ("4Runner",      "SUV",       37000),
    ("Sequoia",      "SUV",       58000),
    ("Land Cruiser", "SUV",       56000),
    ("Venza",        "SUV",       33000),
    ("Crown",        "Sedan",     40000),
    ("bZ4X",         "SUV",       43000),
    ("Tacoma",       "Truck",     28000),
    ("Tundra",       "Truck",     36000),
    ("Sienna",       "Minivan",   35000),
    ("86",           "Sports Car",28000),
    ("GR86",         "Sports Car",28000),
    ("Supra",        "Sports Car",44000),
    ("C-HR",         "SUV",       22000),
    ("Corolla Cross","SUV",       23000),
]
MODEL_YEARS = {
    "Avalon": range(2018, 2023),  # discontinued
    "86": range(2018, 2022),      # replaced by GR86
    "GR86": range(2022, 2027),
    "Supra": range(2020, 2027),
    "Venza": range(2021, 2027),   # reintroduced
    "Crown": range(2023, 2027),
    "bZ4X": range(2023, 2027),
    "C-HR": range(2018, 2023),
    "Corolla Cross": range(2022, 2027),
    "Land Cruiser": range(2022, 2027),  # reintroduced
    "RAV4 Prime": range(2021, 2027),
}
KBB_2024 = {
    "Camry": 28500, "Corolla": 23500, "Avalon": 33000, "Prius": 31000,
    "RAV4": 33000, "RAV4 Hybrid": 37500, "RAV4 Prime": 44000,
    "Highlander": 42000, "4Runner": 46000, "Sequoia": 68000,
    "Land Cruiser": 60000, "Venza": 37000, "Crown": 42000,
    "bZ4X": 42000, "Tacoma": 38000, "Tundra": 48000, "Sienna": 42000,
    "86": 27000, "GR86": 31000, "Supra": 50000, "C-HR": 24000,
    "Corolla Cross": 26000,
}
DEFAULT_YEARS = range(2018, 2027)
for model, body_type, msrp in toyota_models:
    year_range = MODEL_YEARS.get(model, DEFAULT_YEARS)
    kbb = KBB_2024.get(model)
    for year in year_range:
        VEHICLES.append((year, "Toyota", model, body_type, msrp, kbb))

# ── HONDA ──────────────────────────────────────────────────────────────────
honda_models = [
    ("Accord",       "Sedan",  27000, 32000),
    ("Civic",        "Sedan",  22000, 26000),
    ("Insight",      "Sedan",  23000, None),   # discontinued 2022
    ("CR-V",         "SUV",    29000, 35000),
    ("CR-V Hybrid",  "SUV",    33000, 38000),
    ("HR-V",         "SUV",    24000, 27000),
    ("Passport",     "SUV",    37000, 42000),
    ("Pilot",        "SUV",    39000, 47000),
    ("Ridgeline",    "Truck",  38000, 45000),
    ("Odyssey",      "Minivan",36000, 42000),
    ("Fit",          "Hatchback",17000,None),  # discontinued 2020
    ("Prologue",     "SUV",    48000, 48000),
]
MODEL_YEARS_H = {
    "Insight": range(2018, 2023),
    "Fit": range(2018, 2021),
    "CR-V Hybrid": range(2020, 2027),
    "Prologue": range(2024, 2027),
}
for model, body_type, msrp, kbb in honda_models:
    for year in MODEL_YEARS_H.get(model, DEFAULT_YEARS):
        VEHICLES.append((year, "Honda", model, body_type, msrp, kbb))

# ── FORD ───────────────────────────────────────────────────────────────────
ford_data = [
    ("Mustang",      "Sports Car", 28000, 36000, DEFAULT_YEARS),
    ("Mustang Mach-E","SUV",       44000, 42000, range(2021,2027)),
    ("F-150",        "Truck",      28000, 46000, DEFAULT_YEARS),
    ("F-150 Lightning","Truck",    56000, 55000, range(2022,2027)),
    ("Ranger",       "Truck",      25000, 36000, range(2019,2027)),
    ("Maverick",     "Truck",      23000, 29000, range(2022,2027)),
    ("Explorer",     "SUV",        36000, 44000, DEFAULT_YEARS),
    ("Escape",       "SUV",        27000, 31000, DEFAULT_YEARS),
    ("Edge",         "SUV",        35000, 37000, range(2018,2024)),
    ("Expedition",   "SUV",        54000, 64000, DEFAULT_YEARS),
    ("Bronco",       "SUV",        31000, 42000, range(2021,2027)),
    ("Bronco Sport", "SUV",        28000, 34000, range(2021,2027)),
    ("EcoSport",     "SUV",        20000, None,  range(2018,2023)),
    ("Fusion",       "Sedan",      24000, None,  range(2018,2021)),
]
for model, body_type, msrp, kbb, years in ford_data:
    for year in years:
        VEHICLES.append((year, "Ford", model, body_type, msrp, kbb))

# ── CHEVROLET ──────────────────────────────────────────────────────────────
chevy_data = [
    ("Malibu",       "Sedan",     22000, None,  range(2018,2024)),
    ("Camaro",       "Sports Car",25000, 32000, range(2018,2025)),
    ("Corvette",     "Sports Car",58000, 72000, DEFAULT_YEARS),
    ("Equinox",      "SUV",       27000, 31000, DEFAULT_YEARS),
    ("Equinox EV",   "SUV",       35000, 35000, range(2024,2027)),
    ("Trax",         "SUV",       21000, 24000, DEFAULT_YEARS),
    ("Trailblazer",  "SUV",       23000, 27000, range(2021,2027)),
    ("Blazer",       "SUV",       33000, 38000, range(2019,2027)),
    ("Blazer EV",    "SUV",       44000, 44000, range(2024,2027)),
    ("Traverse",     "SUV",       34000, 42000, DEFAULT_YEARS),
    ("Tahoe",        "SUV",       51000, 62000, DEFAULT_YEARS),
    ("Suburban",     "SUV",       54000, 66000, DEFAULT_YEARS),
    ("Colorado",     "Truck",     26000, 35000, DEFAULT_YEARS),
    ("Silverado 1500","Truck",    28000, 46000, DEFAULT_YEARS),
    ("Silverado EV", "Truck",     40000, 40000, range(2024,2027)),
    ("Bolt EV",      "Hatchback", 37500, 27000, range(2017,2024)),
    ("Bolt EUV",     "SUV",       28000, 27000, range(2022,2024)),
    ("Spark",        "Hatchback", 14000, None,  range(2018,2023)),
    ("Encore",       "SUV",       23000, None,  range(2018,2023)),
    ("Encore GX",    "SUV",       24000, 27000, range(2020,2027)),
]
for model, body_type, msrp, kbb, years in chevy_data:
    for year in years:
        VEHICLES.append((year, "Chevrolet", model, body_type, msrp, kbb))

# ── GMC ───────────────────────────────────────────────────────────────────
gmc_data = [
    ("Terrain",     "SUV",   28000, 33000, DEFAULT_YEARS),
    ("Acadia",      "SUV",   35000, 42000, DEFAULT_YEARS),
    ("Yukon",       "SUV",   52000, 64000, DEFAULT_YEARS),
    ("Yukon XL",    "SUV",   55000, 67000, DEFAULT_YEARS),
    ("Sierra 1500", "Truck", 29000, 48000, DEFAULT_YEARS),
    ("Sierra EV",   "Truck", 50000, 50000, range(2024,2027)),
    ("Canyon",      "Truck", 28000, 38000, DEFAULT_YEARS),
    ("Envoy",       "SUV",   35000, 35000, range(2024,2027)),
    ("Hummer EV",   "Truck", 80000, 85000, range(2022,2027)),
    ("Hummer EV SUV","SUV",  80000, 82000, range(2022,2027)),
]
for model, body_type, msrp, kbb, years in gmc_data:
    for year in years:
        VEHICLES.append((year, "GMC", model, body_type, msrp, kbb))

# ── RAM ───────────────────────────────────────────────────────────────────
for year in DEFAULT_YEARS:
    VEHICLES.append((year, "Ram", "1500", "Truck", 33000, 48000))
for year in range(2024, 2027):
    VEHICLES.append((year, "Ram", "1500 REV", "Truck", 58000, 58000))

# ── JEEP ──────────────────────────────────────────────────────────────────
jeep_data = [
    ("Wrangler",     "SUV",   29000, 42000, DEFAULT_YEARS),
    ("Wrangler 4xe", "SUV",   54000, 52000, range(2021,2027)),
    ("Grand Cherokee","SUV",  38000, 48000, DEFAULT_YEARS),
    ("Grand Cherokee 4xe","SUV",59000,56000,range(2022,2027)),
    ("Cherokee",     "SUV",   28000, None,  range(2018,2024)),
    ("Compass",      "SUV",   26000, 30000, DEFAULT_YEARS),
    ("Renegade",     "SUV",   23000, 26000, DEFAULT_YEARS),
    ("Gladiator",    "Truck", 35000, 42000, range(2020,2027)),
    ("Grand Wagoneer","SUV",  88000, 92000, range(2022,2027)),
    ("Wagoneer",     "SUV",   58000, 62000, range(2022,2027)),
    ("Avenger",      "SUV",   25000, None,  range(2023,2027)),
    ("Recon",        "SUV",   50000, 50000, range(2025,2027)),
]
for model, body_type, msrp, kbb, years in jeep_data:
    for year in years:
        VEHICLES.append((year, "Jeep", model, body_type, msrp, kbb))

# ── DODGE ─────────────────────────────────────────────────────────────────
dodge_data = [
    ("Charger",      "Sedan",     30000, 36000, DEFAULT_YEARS),
    ("Challenger",   "Sports Car",28000, 36000, range(2018,2024)),
    ("Durango",      "SUV",       36000, 46000, DEFAULT_YEARS),
    ("Hornet",       "SUV",       30000, 32000, range(2023,2027)),
]
for model, body_type, msrp, kbb, years in dodge_data:
    for year in years:
        VEHICLES.append((year, "Dodge", model, body_type, msrp, kbb))

# ── NISSAN ─────────────────────────────────────────────────────────────────
nissan_data = [
    ("Altima",      "Sedan",  24000, 28000, DEFAULT_YEARS),
    ("Sentra",      "Sedan",  20000, 22000, DEFAULT_YEARS),
    ("Maxima",      "Sedan",  35000, None,  range(2018,2024)),
    ("Versa",       "Sedan",  15000, 18000, DEFAULT_YEARS),
    ("Rogue",       "SUV",    27000, 33000, DEFAULT_YEARS),
    ("Rogue Sport",  "SUV",   24000, None,  range(2018,2023)),
    ("Murano",      "SUV",    33000, 38000, DEFAULT_YEARS),
    ("Pathfinder",  "SUV",    34000, 41000, DEFAULT_YEARS),
    ("Armada",      "SUV",    48000, 57000, DEFAULT_YEARS),
    ("Kicks",       "SUV",    20000, 23000, range(2018,2027)),
    ("Frontier",    "Truck",  29000, 36000, DEFAULT_YEARS),
    ("Titan",       "Truck",  36000, 45000, DEFAULT_YEARS),
    ("Leaf",        "Hatchback",28000,22000, DEFAULT_YEARS),
    ("Ariya",       "SUV",    44000, 43000, range(2023,2027)),
    ("Z",           "Sports Car",41000,46000,range(2023,2027)),
    ("370Z",        "Sports Car",30000,None, range(2018,2022)),
]
for model, body_type, msrp, kbb, years in nissan_data:
    for year in years:
        VEHICLES.append((year, "Nissan", model, body_type, msrp, kbb))

# ── HYUNDAI ────────────────────────────────────────────────────────────────
hyundai_data = [
    ("Elantra",     "Sedan",  20000, 24000, DEFAULT_YEARS),
    ("Sonata",      "Sedan",  25000, 27000, DEFAULT_YEARS),
    ("Tucson",      "SUV",    26000, 32000, DEFAULT_YEARS),
    ("Santa Fe",    "SUV",    29000, 36000, DEFAULT_YEARS),
    ("Palisade",    "SUV",    35000, 43000, range(2020,2027)),
    ("Venue",       "SUV",    19000, 22000, range(2020,2027)),
    ("Kona",        "SUV",    22000, 26000, DEFAULT_YEARS),
    ("Kona Electric","SUV",   34000, 33000, range(2019,2027)),
    ("Ioniq",       "Sedan",  23000, None,  range(2018,2022)),
    ("Ioniq 5",     "SUV",    41000, 43000, range(2022,2027)),
    ("Ioniq 6",     "Sedan",  38000, 40000, range(2023,2027)),
    ("Ioniq 9",     "SUV",    60000, 60000, range(2026,2027)),
    ("Nexo",        "SUV",    59000, None,  range(2019,2027)),
    ("Accent",      "Sedan",  16000, None,  range(2018,2023)),
    ("Veloster",    "Hatchback",19000,None, range(2018,2022)),
    ("Santa Cruz",  "Truck",  25000, 32000, range(2022,2027)),
]
for model, body_type, msrp, kbb, years in hyundai_data:
    for year in years:
        VEHICLES.append((year, "Hyundai", model, body_type, msrp, kbb))

# ── KIA ────────────────────────────────────────────────────────────────────
kia_data = [
    ("Forte",       "Sedan",  19000, 22000, DEFAULT_YEARS),
    ("K5",          "Sedan",  24000, 27000, range(2021,2027)),
    ("Optima",      "Sedan",  24000, None,  range(2018,2021)),
    ("Stinger",     "Sedan",  33000, None,  range(2018,2024)),
    ("Niro",        "SUV",    25000, 29000, DEFAULT_YEARS),
    ("Niro EV",     "SUV",    40000, 38000, range(2019,2027)),
    ("Sportage",    "SUV",    27000, 33000, DEFAULT_YEARS),
    ("Sorento",     "SUV",    29000, 37000, DEFAULT_YEARS),
    ("Telluride",   "SUV",    33000, 44000, range(2020,2027)),
    ("Soul",        "SUV",    20000, 24000, DEFAULT_YEARS),
    ("Seltos",      "SUV",    23000, 27000, range(2021,2027)),
    ("EV6",         "SUV",    42000, 44000, range(2022,2027)),
    ("EV9",         "SUV",    55000, 57000, range(2024,2027)),
    ("Carnival",    "Minivan",33000, 39000, range(2022,2027)),
    ("Sedona",      "Minivan",30000, None,  range(2018,2022)),
    ("Rio",         "Sedan",  16000, None,  range(2018,2023)),
    ("Cadenza",     "Sedan",  33000, None,  range(2018,2021)),
]
for model, body_type, msrp, kbb, years in kia_data:
    for year in years:
        VEHICLES.append((year, "Kia", model, body_type, msrp, kbb))

# ── SUBARU ─────────────────────────────────────────────────────────────────
subaru_data = [
    ("Impreza",     "Sedan",  19000, 23000, DEFAULT_YEARS),
    ("Legacy",      "Sedan",  22000, 25000, DEFAULT_YEARS),
    ("Outback",     "Wagon",  27000, 33000, DEFAULT_YEARS),
    ("Forester",    "SUV",    25000, 31000, DEFAULT_YEARS),
    ("Crosstrek",   "SUV",    22000, 28000, DEFAULT_YEARS),
    ("Ascent",      "SUV",    34000, 40000, range(2019,2027)),
    ("BRZ",         "Sports Car",28000,32000,DEFAULT_YEARS),
    ("WRX",         "Sedan",  28000, 32000, DEFAULT_YEARS),
    ("Solterra",    "SUV",    44000, 42000, range(2023,2027)),
    ("Baja",        "Truck",  None,  None,  range(2018,2018)),
]
for model, body_type, msrp, kbb, years in subaru_data:
    for year in years:
        VEHICLES.append((year, "Subaru", model, body_type, msrp, kbb))

# ── MAZDA ─────────────────────────────────────────────────────────────────
mazda_data = [
    ("Mazda3",      "Sedan",  22000, 27000, DEFAULT_YEARS),
    ("Mazda6",      "Sedan",  24000, None,  range(2018,2022)),
    ("CX-3",        "SUV",    21000, None,  range(2018,2022)),
    ("CX-30",       "SUV",    22000, 27000, range(2020,2027)),
    ("CX-5",        "SUV",    26000, 32000, DEFAULT_YEARS),
    ("CX-50",       "SUV",    28000, 34000, range(2023,2027)),
    ("CX-9",        "SUV",    34000, None,  range(2018,2024)),
    ("CX-90",       "SUV",    40000, 43000, range(2024,2027)),
    ("MX-5 Miata",  "Convertible",27000,31000,DEFAULT_YEARS),
    ("MX-30",       "SUV",    34000, None,  range(2022,2026)),
]
for model, body_type, msrp, kbb, years in mazda_data:
    for year in years:
        VEHICLES.append((year, "Mazda", model, body_type, msrp, kbb))

# ── VOLKSWAGEN ─────────────────────────────────────────────────────────────
vw_data = [
    ("Jetta",       "Sedan",  20000, 24000, DEFAULT_YEARS),
    ("Passat",      "Sedan",  25000, None,  range(2018,2023)),
    ("Arteon",      "Sedan",  36000, None,  range(2019,2024)),
    ("Golf",        "Hatchback",23000,None, range(2018,2022)),
    ("Golf GTI",    "Hatchback",30000,36000,DEFAULT_YEARS),
    ("Golf R",      "Hatchback",43000,47000,DEFAULT_YEARS),
    ("Tiguan",      "SUV",    25000, 32000, DEFAULT_YEARS),
    ("Atlas",       "SUV",    35000, 40000, DEFAULT_YEARS),
    ("Atlas Cross Sport","SUV",34000,39000, range(2020,2027)),
    ("ID.4",        "SUV",    40000, 40000, range(2021,2027)),
    ("ID.Buzz",     "Minivan",60000, 60000, range(2024,2027)),
    ("Taos",        "SUV",    24000, 28000, range(2022,2027)),
]
for model, body_type, msrp, kbb, years in vw_data:
    for year in years:
        VEHICLES.append((year, "Volkswagen", model, body_type, msrp, kbb))

# ── BMW ────────────────────────────────────────────────────────────────────
bmw_data = [
    ("2 Series",    "Coupe",  36000, 44000, DEFAULT_YEARS),
    ("3 Series",    "Sedan",  41000, 49000, DEFAULT_YEARS),
    ("4 Series",    "Coupe",  46000, 54000, range(2021,2027)),
    ("5 Series",    "Sedan",  54000, 63000, DEFAULT_YEARS),
    ("7 Series",    "Sedan",  93000, 105000,DEFAULT_YEARS),
    ("8 Series",    "Coupe",  86000, 96000, range(2019,2027)),
    ("X1",          "SUV",    37000, 44000, DEFAULT_YEARS),
    ("X2",          "SUV",    38000, 44000, DEFAULT_YEARS),
    ("X3",          "SUV",    45000, 54000, DEFAULT_YEARS),
    ("X4",          "SUV",    51000, 59000, DEFAULT_YEARS),
    ("X5",          "SUV",    61000, 73000, DEFAULT_YEARS),
    ("X6",          "SUV",    66000, 77000, DEFAULT_YEARS),
    ("X7",          "SUV",    76000, 90000, range(2019,2027)),
    ("i3",          "Hatchback",44000,None, range(2018,2022)),
    ("i4",          "Sedan",  65000, 68000, range(2022,2027)),
    ("i5",          "Sedan",  67000, 70000, range(2024,2027)),
    ("i7",          "Sedan",  106000,112000,range(2023,2027)),
    ("iX",          "SUV",    87000, 89000, range(2022,2027)),
    ("iX1",         "SUV",    37000, 40000, range(2023,2027)),
    ("iX3",         "SUV",    None,  None,  range(2022,2025)),
    ("M2",          "Sports Car",63000,72000,DEFAULT_YEARS),
    ("M3",          "Sedan",  73000, 86000, DEFAULT_YEARS),
    ("M4",          "Coupe",  74000, 88000, range(2021,2027)),
    ("M5",          "Sedan",  109000,122000,DEFAULT_YEARS),
    ("M8",          "Coupe",  133000,140000,range(2019,2027)),
    ("Z4",          "Convertible",50000,58000,range(2019,2027)),
]
for model, body_type, msrp, kbb, years in bmw_data:
    for year in years:
        VEHICLES.append((year, "BMW", model, body_type, msrp, kbb))

# ── MERCEDES-BENZ ──────────────────────────────────────────────────────────
mb_data = [
    ("A-Class",     "Sedan",  33000, None,  range(2019,2024)),
    ("C-Class",     "Sedan",  43000, 53000, DEFAULT_YEARS),
    ("E-Class",     "Sedan",  55000, 65000, DEFAULT_YEARS),
    ("S-Class",     "Sedan",  111000,125000,DEFAULT_YEARS),
    ("CLA",         "Sedan",  38000, 44000, DEFAULT_YEARS),
    ("CLS",         "Sedan",  69000, None,  range(2019,2024)),
    ("GLA",         "SUV",    36000, 44000, range(2021,2027)),
    ("GLB",         "SUV",    38000, 46000, range(2020,2027)),
    ("GLC",         "SUV",    45000, 55000, DEFAULT_YEARS),
    ("GLE",         "SUV",    57000, 68000, DEFAULT_YEARS),
    ("GLS",         "SUV",    90000, 105000,DEFAULT_YEARS),
    ("G-Class",     "SUV",    131000,145000,DEFAULT_YEARS),
    ("EQB",         "SUV",    54000, 52000, range(2022,2027)),
    ("EQE",         "Sedan",  74000, 70000, range(2023,2027)),
    ("EQE SUV",     "SUV",    78000, 74000, range(2023,2027)),
    ("EQS",         "Sedan",  104000,95000, range(2022,2027)),
    ("EQS SUV",     "SUV",    105000,98000, range(2023,2027)),
    ("AMG GT",      "Sports Car",116000,130000,DEFAULT_YEARS),
    ("SL",          "Convertible",91000,100000,range(2022,2027)),
    ("Sprinter",    "Van",    40000, None,  DEFAULT_YEARS),
]
for model, body_type, msrp, kbb, years in mb_data:
    for year in years:
        VEHICLES.append((year, "Mercedes-Benz", model, body_type, msrp, kbb))

# ── AUDI ──────────────────────────────────────────────────────────────────
audi_data = [
    ("A3",          "Sedan",  34000, 40000, DEFAULT_YEARS),
    ("A4",          "Sedan",  39000, 47000, DEFAULT_YEARS),
    ("A5",          "Coupe",  44000, 52000, DEFAULT_YEARS),
    ("A6",          "Sedan",  55000, 65000, DEFAULT_YEARS),
    ("A7",          "Sedan",  69000, 79000, DEFAULT_YEARS),
    ("A8",          "Sedan",  86000, 98000, DEFAULT_YEARS),
    ("Q3",          "SUV",    35000, 43000, DEFAULT_YEARS),
    ("Q4 e-tron",   "SUV",    45000, 47000, range(2022,2027)),
    ("Q5",          "SUV",    43000, 53000, DEFAULT_YEARS),
    ("Q7",          "SUV",    55000, 65000, DEFAULT_YEARS),
    ("Q8",          "SUV",    68000, 78000, range(2019,2027)),
    ("Q8 e-tron",   "SUV",    74000, 72000, range(2024,2027)),
    ("e-tron",      "SUV",    65000, None,  range(2019,2024)),
    ("e-tron GT",   "Sedan",  102000,105000,range(2022,2027)),
    ("RS3",         "Sedan",  59000, 68000, range(2022,2027)),
    ("RS5",         "Coupe",  74000, 82000, DEFAULT_YEARS),
    ("RS6",         "Wagon",  118000,130000,range(2020,2027)),
    ("RS7",         "Sedan",  118000,130000,DEFAULT_YEARS),
    ("R8",          "Sports Car",158000,165000,range(2018,2024)),
    ("TT",          "Coupe",  46000, None,  range(2018,2024)),
    ("S3",          "Sedan",  47000, 54000, range(2022,2027)),
    ("S4",          "Sedan",  52000, 61000, DEFAULT_YEARS),
    ("S5",          "Coupe",  57000, 66000, DEFAULT_YEARS),
    ("SQ5",         "SUV",    55000, 65000, DEFAULT_YEARS),
    ("SQ7",         "SUV",    70000, 80000, range(2020,2027)),
    ("SQ8",         "SUV",    88000, 96000, range(2021,2027)),
]
for model, body_type, msrp, kbb, years in audi_data:
    for year in years:
        VEHICLES.append((year, "Audi", model, body_type, msrp, kbb))

# ── LEXUS ─────────────────────────────────────────────────────────────────
lexus_data = [
    ("IS",          "Sedan",  39000, 46000, DEFAULT_YEARS),
    ("ES",          "Sedan",  40000, 48000, DEFAULT_YEARS),
    ("LS",          "Sedan",  76000, 86000, DEFAULT_YEARS),
    ("UX",          "SUV",    33000, 38000, range(2019,2027)),
    ("NX",          "SUV",    37000, 46000, DEFAULT_YEARS),
    ("RX",          "SUV",    46000, 56000, DEFAULT_YEARS),
    ("GX",          "SUV",    53000, 63000, DEFAULT_YEARS),
    ("LX",          "SUV",    86000, 98000, DEFAULT_YEARS),
    ("LC",          "Coupe",  93000, 95000, DEFAULT_YEARS),
    ("RC",          "Coupe",  42000, None,  range(2018,2025)),
    ("RZ",          "SUV",    55000, 55000, range(2023,2027)),
    ("TX",          "SUV",    52000, 52000, range(2024,2027)),
    ("GX 550",      "SUV",    65000, 65000, range(2024,2027)),
]
for model, body_type, msrp, kbb, years in lexus_data:
    for year in years:
        VEHICLES.append((year, "Lexus", model, body_type, msrp, kbb))

# ── ACURA ─────────────────────────────────────────────────────────────────
acura_data = [
    ("ILX",         "Sedan",  25000, None,  range(2018,2023)),
    ("TLX",         "Sedan",  37000, 44000, DEFAULT_YEARS),
    ("RDX",         "SUV",    38000, 46000, DEFAULT_YEARS),
    ("MDX",         "SUV",    47000, 55000, DEFAULT_YEARS),
    ("NSX",         "Sports Car",157000,None,range(2018,2023)),
    ("Integra",     "Sedan",  31000, 35000, range(2023,2027)),
    ("ZDX",         "SUV",    65000, 65000, range(2024,2027)),
]
for model, body_type, msrp, kbb, years in acura_data:
    for year in years:
        VEHICLES.append((year, "Acura", model, body_type, msrp, kbb))

# ── INFINITI ──────────────────────────────────────────────────────────────
infiniti_data = [
    ("Q50",         "Sedan",  37000, 40000, DEFAULT_YEARS),
    ("Q60",         "Coupe",  41000, None,  range(2018,2023)),
    ("QX50",        "SUV",    37000, 40000, DEFAULT_YEARS),
    ("QX55",        "SUV",    45000, 47000, range(2022,2027)),
    ("QX60",        "SUV",    47000, 50000, DEFAULT_YEARS),
    ("QX80",        "SUV",    68000, 73000, DEFAULT_YEARS),
]
for model, body_type, msrp, kbb, years in infiniti_data:
    for year in years:
        VEHICLES.append((year, "Infiniti", model, body_type, msrp, kbb))

# ── CADILLAC ──────────────────────────────────────────────────────────────
cadillac_data = [
    ("CT4",         "Sedan",  33000, 38000, range(2020,2027)),
    ("CT5",         "Sedan",  37000, 44000, range(2020,2027)),
    ("XT4",         "SUV",    35000, 40000, range(2019,2027)),
    ("XT5",         "SUV",    43000, 49000, DEFAULT_YEARS),
    ("XT6",         "SUV",    49000, 55000, range(2020,2027)),
    ("Escalade",    "SUV",    76000, 96000, DEFAULT_YEARS),
    ("Escalade ESV","SUV",    82000, 100000,DEFAULT_YEARS),
    ("LYRIQ",       "SUV",    58000, 58000, range(2023,2027)),
    ("CELESTIQ",    "Sedan",  340000,None,  range(2024,2027)),
    ("OPTIQ",       "SUV",    55000, 55000, range(2025,2027)),
    ("VISTIQ",      "SUV",    78000, 78000, range(2025,2027)),
]
for model, body_type, msrp, kbb, years in cadillac_data:
    for year in years:
        VEHICLES.append((year, "Cadillac", model, body_type, msrp, kbb))

# ── LINCOLN ────────────────────────────────────────────────────────────────
lincoln_data = [
    ("MKZ",         "Sedan",  36000, None,  range(2018,2021)),
    ("Continental", "Sedan",  46000, None,  range(2018,2020)),
    ("Corsair",     "SUV",    36000, 43000, range(2020,2027)),
    ("Nautilus",    "SUV",    44000, 52000, DEFAULT_YEARS),
    ("Aviator",     "SUV",    52000, 62000, range(2020,2027)),
    ("Navigator",   "SUV",    77000, 95000, DEFAULT_YEARS),
]
for model, body_type, msrp, kbb, years in lincoln_data:
    for year in years:
        VEHICLES.append((year, "Lincoln", model, body_type, msrp, kbb))

# ── BUICK ─────────────────────────────────────────────────────────────────
buick_data = [
    ("Encore",      "SUV",    23000, None,  range(2018,2023)),
    ("Encore GX",   "SUV",    25000, 28000, range(2020,2027)),
    ("Envision",    "SUV",    32000, 37000, DEFAULT_YEARS),
    ("Enclave",     "SUV",    42000, 49000, DEFAULT_YEARS),
    ("Envista",     "SUV",    24000, 26000, range(2024,2027)),
    ("Electra E4",  "SUV",    None,  None,  range(2025,2027)),
]
for model, body_type, msrp, kbb, years in buick_data:
    for year in years:
        VEHICLES.append((year, "Buick", model, body_type, msrp, kbb))

# ── CHRYSLER ──────────────────────────────────────────────────────────────
chrysler_data = [
    ("300",         "Sedan",  29000, None,  range(2018,2024)),
    ("Pacifica",    "Minivan",37000, 40000, DEFAULT_YEARS),
    ("Voyager",     "Minivan",27000, None,  range(2020,2023)),
    ("Airflow",     "SUV",    None,  None,  range(2025,2027)),
]
for model, body_type, msrp, kbb, years in chrysler_data:
    for year in years:
        VEHICLES.append((year, "Chrysler", model, body_type, msrp, kbb))

# ── TESLA ─────────────────────────────────────────────────────────────────
tesla_data = [
    ("Model 3",     "Sedan",  35000, 38000, DEFAULT_YEARS),
    ("Model S",     "Sedan",  74000, 80000, DEFAULT_YEARS),
    ("Model X",     "SUV",    79000, 86000, DEFAULT_YEARS),
    ("Model Y",     "SUV",    40000, 43000, range(2020,2027)),
    ("Cybertruck",  "Truck",  60000, 70000, range(2024,2027)),
    ("Roadster",    "Sports Car",200000,None,range(2025,2027)),
]
for model, body_type, msrp, kbb, years in tesla_data:
    for year in years:
        VEHICLES.append((year, "Tesla", model, body_type, msrp, kbb))

# ── RIVIAN ─────────────────────────────────────────────────────────────────
rivian_data = [
    ("R1T",         "Truck",  67500, 68000, range(2022,2027)),
    ("R1S",         "SUV",    72000, 73000, range(2022,2027)),
    ("R2",          "SUV",    45000, 45000, range(2026,2027)),
]
for model, body_type, msrp, kbb, years in rivian_data:
    for year in years:
        VEHICLES.append((year, "Rivian", model, body_type, msrp, kbb))

# ── VOLVO ─────────────────────────────────────────────────────────────────
volvo_data = [
    ("S60",         "Sedan",  38000, 44000, DEFAULT_YEARS),
    ("S90",         "Sedan",  53000, 60000, DEFAULT_YEARS),
    ("V60",         "Wagon",  44000, 48000, DEFAULT_YEARS),
    ("V90",         "Wagon",  56000, None,  DEFAULT_YEARS),
    ("XC40",        "SUV",    35000, 42000, range(2019,2027)),
    ("XC40 Recharge","SUV",   53000, 50000, range(2021,2027)),
    ("XC60",        "SUV",    43000, 51000, DEFAULT_YEARS),
    ("XC90",        "SUV",    56000, 66000, DEFAULT_YEARS),
    ("EX30",        "SUV",    34000, 34000, range(2024,2027)),
    ("EX90",        "SUV",    77000, 77000, range(2025,2027)),
    ("C40 Recharge","SUV",    54000, 50000, range(2022,2027)),
]
for model, body_type, msrp, kbb, years in volvo_data:
    for year in years:
        VEHICLES.append((year, "Volvo", model, body_type, msrp, kbb))

# ── PORSCHE ────────────────────────────────────────────────────────────────
porsche_data = [
    ("Macan",       "SUV",    52000, 60000, DEFAULT_YEARS),
    ("Macan Electric","SUV",  75000, 75000, range(2024,2027)),
    ("Cayenne",     "SUV",    68000, 82000, DEFAULT_YEARS),
    ("Cayenne Coupe","SUV",   75000, 88000, range(2020,2027)),
    ("Taycan",      "Sedan",  82000, 90000, range(2020,2027)),
    ("Taycan Cross Turismo","Wagon",85000,92000,range(2021,2027)),
    ("Taycan Sport Turismo","Wagon",85000,92000,range(2022,2027)),
    ("911",         "Sports Car",106000,122000,DEFAULT_YEARS),
    ("718 Cayman",  "Sports Car",61000,72000, DEFAULT_YEARS),
    ("718 Boxster", "Convertible",62000,74000,DEFAULT_YEARS),
    ("Panamera",    "Sedan",  88000, 100000,DEFAULT_YEARS),
]
for model, body_type, msrp, kbb, years in porsche_data:
    for year in years:
        VEHICLES.append((year, "Porsche", model, body_type, msrp, kbb))

# ── GENESIS ────────────────────────────────────────────────────────────────
genesis_data = [
    ("G70",         "Sedan",  35000, 41000, range(2019,2027)),
    ("G80",         "Sedan",  48000, 56000, DEFAULT_YEARS),
    ("G90",         "Sedan",  87000, 97000, DEFAULT_YEARS),
    ("GV70",        "SUV",    41000, 49000, range(2022,2027)),
    ("GV80",        "SUV",    51000, 59000, range(2021,2027)),
    ("GV60",        "SUV",    47000, 47000, range(2023,2027)),
    ("G80 Electric","Sedan",  80000, 78000, range(2023,2027)),
    ("GV70 Electrified","SUV",67000,65000, range(2023,2027)),
    ("GV90",        "SUV",    100000,None,  range(2026,2027)),
]
for model, body_type, msrp, kbb, years in genesis_data:
    for year in years:
        VEHICLES.append((year, "Genesis", model, body_type, msrp, kbb))

# ── LAND ROVER ─────────────────────────────────────────────────────────────
lr_data = [
    ("Discovery",   "SUV",    53000, 60000, DEFAULT_YEARS),
    ("Discovery Sport","SUV", 43000, 48000, DEFAULT_YEARS),
    ("Range Rover Sport","SUV",68000,80000, DEFAULT_YEARS),
    ("Range Rover Velar","SUV",58000,65000,DEFAULT_YEARS),
    ("Range Rover Evoque","SUV",44000,50000,DEFAULT_YEARS),
    ("Range Rover", "SUV",    92000, 108000,DEFAULT_YEARS),
    ("Defender",    "SUV",    47000, 58000, range(2020,2027)),
]
for model, body_type, msrp, kbb, years in lr_data:
    for year in years:
        VEHICLES.append((year, "Land Rover", model, body_type, msrp, kbb))

# ── JAGUAR ────────────────────────────────────────────────────────────────
jag_data = [
    ("XE",          "Sedan",  35000, None,  range(2018,2023)),
    ("XF",          "Sedan",  46000, None,  range(2018,2024)),
    ("F-Type",      "Sports Car",62000,None,range(2018,2025)),
    ("E-Pace",      "SUV",    42000, None,  range(2018,2024)),
    ("F-Pace",      "SUV",    48000, None,  range(2018,2025)),
    ("I-Pace",      "SUV",    69000, None,  range(2019,2024)),
    ("Type 00",     "Sports Car",None,None, range(2026,2027)),
]
for model, body_type, msrp, kbb, years in jag_data:
    for year in years:
        VEHICLES.append((year, "Jaguar", model, body_type, msrp, kbb))

# ── MINI ──────────────────────────────────────────────────────────────────
mini_data = [
    ("Hardtop",     "Hatchback",22000,26000, DEFAULT_YEARS),
    ("Convertible", "Convertible",26000,30000,DEFAULT_YEARS),
    ("Clubman",     "Wagon",  27000, None,  range(2018,2025)),
    ("Countryman",  "SUV",    28000, 35000, DEFAULT_YEARS),
    ("Paceman",     "SUV",    None,  None,  range(2018,2018)),
    ("Cooper SE",   "Hatchback",29000,28000,range(2020,2024)),
    ("Aceman",      "SUV",    35000, None,  range(2025,2027)),
    ("John Cooper Works","Hatchback",33000,38000,DEFAULT_YEARS),
]
for model, body_type, msrp, kbb, years in mini_data:
    for year in years:
        VEHICLES.append((year, "MINI", model, body_type, msrp, kbb))

# ── MITSUBISHI ─────────────────────────────────────────────────────────────
mits_data = [
    ("Outlander",   "SUV",    26000, 30000, DEFAULT_YEARS),
    ("Outlander PHEV","SUV",  36000, 38000, range(2018,2027)),
    ("Eclipse Cross","SUV",   24000, 27000, range(2018,2027)),
    ("Galant",      "Sedan",  None,  None,  range(2018,2018)),
    ("Mirage",      "Hatchback",15000,None, DEFAULT_YEARS),
    ("Outlander Sport","SUV", 22000, None,  range(2018,2025)),
]
for model, body_type, msrp, kbb, years in mits_data:
    for year in years:
        VEHICLES.append((year, "Mitsubishi", model, body_type, msrp, kbb))

# ── ALFA ROMEO ─────────────────────────────────────────────────────────────
alfa_data = [
    ("Giulia",      "Sedan",  44000, 46000, DEFAULT_YEARS),
    ("Stelvio",     "SUV",    44000, 48000, DEFAULT_YEARS),
    ("4C",          "Sports Car",61000,None,range(2018,2020)),
    ("Tonale",      "SUV",    43000, 43000, range(2023,2027)),
    ("Junior",      "SUV",    None,  None,  range(2026,2027)),
]
for model, body_type, msrp, kbb, years in alfa_data:
    for year in years:
        VEHICLES.append((year, "Alfa Romeo", model, body_type, msrp, kbb))

# ── FIAT ──────────────────────────────────────────────────────────────────
fiat_data = [
    ("500",         "Hatchback",16000,None, range(2018,2021)),
    ("500X",        "SUV",    22000, None,  range(2018,2023)),
    ("500L",        "Hatchback",20000,None, range(2018,2021)),
    ("500e",        "Hatchback",33000,None, range(2024,2027)),
    ("Panda",       "Hatchback",None, None, range(2025,2027)),
]
for model, body_type, msrp, kbb, years in fiat_data:
    for year in years:
        VEHICLES.append((year, "Fiat", model, body_type, msrp, kbb))

# ── MASERATI ──────────────────────────────────────────────────────────────
mas_data = [
    ("Ghibli",      "Sedan",  75000, None,  range(2018,2024)),
    ("Quattroporte","Sedan",  107000,None,  range(2018,2024)),
    ("Levante",     "SUV",    75000, None,  range(2018,2024)),
    ("Grecale",     "SUV",    63000, 65000, range(2023,2027)),
    ("GranTurismo", "Sports Car",178000,None,range(2023,2027)),
    ("MC20",        "Sports Car",210000,None,range(2022,2027)),
]
for model, body_type, msrp, kbb, years in mas_data:
    for year in years:
        VEHICLES.append((year, "Maserati", model, body_type, msrp, kbb))

# ── LAMBORGHINI ────────────────────────────────────────────────────────────
lamb_data = [
    ("Huracan",     "Sports Car",201000,None,range(2018,2025)),
    ("Urus",        "SUV",    218000,None,  range(2019,2027)),
    ("Revuelto",    "Sports Car",500000,None,range(2024,2027)),
    ("Temerario",   "Sports Car",None,  None, range(2026,2027)),
]
for model, body_type, msrp, kbb, years in lamb_data:
    for year in years:
        VEHICLES.append((year, "Lamborghini", model, body_type, msrp, kbb))

# ── FERRARI ────────────────────────────────────────────────────────────────
ferrari_data = [
    ("488",         "Sports Car",263000,None,range(2018,2020)),
    ("F8",          "Sports Car",276000,None,range(2020,2023)),
    ("Roma",        "Sports Car",222000,None,range(2021,2027)),
    ("Portofino",   "Convertible",215000,None,range(2018,2022)),
    ("GTC4Lusso",   "Wagon",  295000,None,  range(2018,2021)),
    ("SF90 Stradale","Sports Car",507000,None,range(2021,2027)),
    ("296 GTB",     "Sports Car",321000,None,range(2022,2027)),
    ("Purosangue",  "SUV",    400000,None,  range(2023,2027)),
    ("12Cilindri",  "Sports Car",400000,None,range(2025,2027)),
]
for model, body_type, msrp, kbb, years in ferrari_data:
    for year in years:
        VEHICLES.append((year, "Ferrari", model, body_type, msrp, kbb))

# ── ROLLS-ROYCE ────────────────────────────────────────────────────────────
rr_data = [
    ("Ghost",       "Sedan",  311000,None,  DEFAULT_YEARS),
    ("Phantom",     "Sedan",  455000,None,  DEFAULT_YEARS),
    ("Wraith",      "Coupe",  322000,None,  range(2018,2024)),
    ("Dawn",        "Convertible",357000,None,range(2018,2023)),
    ("Cullinan",    "SUV",    330000,None,  range(2019,2027)),
    ("Spectre",     "Coupe",  420000,None,  range(2024,2027)),
    ("Black Badge Ghost","Sedan",383000,None,range(2021,2027)),
]
for model, body_type, msrp, kbb, years in rr_data:
    for year in years:
        VEHICLES.append((year, "Rolls-Royce", model, body_type, msrp, kbb))

# ── BUILD OUTPUT ───────────────────────────────────────────────────────────

def build():
    # Deduplicate
    seen = set()
    unique = []
    for v in VEHICLES:
        key = (v[0], v[1], v[2])
        if key not in seen:
            seen.add(key)
            unique.append(v)

    vehicles_json = []
    for year, make, model, body_type, msrp, kbb in sorted(unique, key=lambda x: (-x[0], x[1], x[2])):
        vehicles_json.append({
            "year": year,
            "make": make,
            "model": model,
            "body_type": body_type,
            "msrp_original": msrp,
            "kbb_fair_purchase_price": kbb,
            "kbb_last_updated": "2024-Q4" if kbb else None,
            "photo_url": None,
            "notes": "",
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "year_range": [2018, 2026],
            "total_vehicles": len(vehicles_json),
            "source": "Curated seed data (NHTSA-aligned) + approximate KBB fair purchase prices",
            "kbb_value_type": "Fair Purchase Price (dealer), approximate 2024 values",
            "notes": "Run scripts/fetch_cars.py to sync with live NHTSA data. Run scripts/update_pricing.py to refresh KBB values.",
        },
        "vehicles": vehicles_json
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    by_type = {}
    for v in vehicles_json:
        by_type.setdefault(v["body_type"], 0)
        by_type[v["body_type"]] += 1

    has_kbb = sum(1 for v in vehicles_json if v["kbb_fair_purchase_price"])
    makes = len(set(v["make"] for v in vehicles_json))
    models = len(set((v["make"], v["model"]) for v in vehicles_json))

    print(f"✅ Seed data written to {OUTPUT_PATH}")
    print(f"   {len(vehicles_json)} total vehicles | {makes} makes | {models} make/model combos")
    print(f"   {has_kbb} have KBB pricing ({len(vehicles_json)-has_kbb} need lookup)")
    print(f"\n   Body type breakdown:")
    for bt, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"     {bt:20s} {count}")


if __name__ == "__main__":
    build()
