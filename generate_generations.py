#!/usr/bin/env python3
"""
generate_generations.py
=======================
Builds data/generations.json — a reference of which generation/refresh
each model is in for each year from 2018–2026.

Generates data/photo_needed.json — the deduplicated list of year+make+model
entries that actually need a unique photo (one per generation).

Logic:
  - Each model is divided into named generations with a year range
  - Within a generation, the "representative year" is the first year
  - photo_needed.json lists only those representative years

Sources: manufacturer announcements, Wikipedia, Car and Driver, Motor Trend
"""

import json
from pathlib import Path
from datetime import datetime

CARS_PATH = Path(__file__).parent.parent / "data" / "cars.json"
GEN_PATH  = Path(__file__).parent.parent / "data" / "generations.json"
OUT_PATH  = Path(__file__).parent.parent / "data" / "photo_needed.json"

# ─────────────────────────────────────────────────────────────────────────────
# GENERATION DATA
# Format: "Make|Model": [ (gen_name, start_year, end_year_inclusive), ... ]
# end_year=2026 means "current / no end in our dataset"
# A "refresh" or "facelift" mid-generation gets its own entry since the
# exterior changes enough to warrant a new photo.
# ─────────────────────────────────────────────────────────────────────────────

GENERATIONS = {

    # ── ACURA ──────────────────────────────────────────────────────────────
    "Acura|ILX":        [("3rd Gen", 2016, 2022)],
    "Acura|TLX":        [("2nd Gen", 2015, 2020), ("3rd Gen", 2021, 2026)],
    "Acura|RDX":        [("3rd Gen", 2019, 2026)],  # 2019 full redesign
    "Acura|MDX":        [("3rd Gen", 2014, 2020), ("4th Gen", 2022, 2026)],
    "Acura|NSX":        [("2nd Gen", 2017, 2022)],
    "Acura|Integra":    [("5th Gen", 2023, 2026)],
    "Acura|ZDX":        [("2nd Gen", 2024, 2026)],

    # ── ALFA ROMEO ─────────────────────────────────────────────────────────
    "Alfa Romeo|Giulia":    [("1st Gen", 2017, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Alfa Romeo|Stelvio":   [("1st Gen", 2017, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Alfa Romeo|4C":        [("1st Gen", 2014, 2020)],
    "Alfa Romeo|Tonale":    [("1st Gen", 2023, 2026)],
    "Alfa Romeo|Junior":    [("1st Gen", 2026, 2026)],

    # ── AUDI ───────────────────────────────────────────────────────────────
    "Audi|A3":          [("8V Facelift", 2017, 2020), ("8Y", 2021, 2026)],
    "Audi|A4":          [("B9 Facelift", 2020, 2026)],   # B9.5 facelift 2020
    "Audi|A5":          [("B9 Facelift", 2020, 2026)],
    "Audi|A6":          [("C8", 2019, 2026)],
    "Audi|A7":          [("C8", 2019, 2026)],
    "Audi|A8":          [("D5 Facelift", 2022, 2026)],
    "Audi|Q3":          [("F3", 2019, 2026)],
    "Audi|Q4 e-tron":   [("1st Gen", 2022, 2026)],
    "Audi|Q5":          [("FY Facelift", 2021, 2026)],
    "Audi|Q7":          [("4M Facelift", 2020, 2026)],
    "Audi|Q8":          [("4M", 2019, 2026)],
    "Audi|Q8 e-tron":   [("1st Gen", 2024, 2026)],
    "Audi|e-tron":      [("1st Gen", 2019, 2023)],
    "Audi|e-tron GT":   [("1st Gen", 2022, 2026)],
    "Audi|RS3":         [("8Y", 2022, 2026)],
    "Audi|RS5":         [("B9 Facelift", 2020, 2026)],
    "Audi|RS6":         [("C8", 2020, 2026)],
    "Audi|RS7":         [("C8", 2020, 2026)],
    "Audi|R8":          [("Type 4S", 2016, 2023)],
    "Audi|TT":          [("8S Facelift", 2019, 2023)],
    "Audi|S3":          [("8Y", 2022, 2026)],
    "Audi|S4":          [("B9 Facelift", 2020, 2026)],
    "Audi|S5":          [("B9 Facelift", 2020, 2026)],
    "Audi|SQ5":         [("FY Facelift", 2021, 2026)],
    "Audi|SQ7":         [("4M Facelift", 2020, 2026)],
    "Audi|SQ8":         [("4M Facelift", 2021, 2026)],

    # ── BMW ────────────────────────────────────────────────────────────────
    "BMW|2 Series":     [("F22 Facelift", 2018, 2021), ("G42", 2022, 2026)],
    "BMW|3 Series":     [("F30 Facelift", 2018, 2018), ("G20", 2019, 2022), ("G20 LCI", 2023, 2026)],
    "BMW|4 Series":     [("G22", 2021, 2026)],
    "BMW|5 Series":     [("G30 Facelift", 2021, 2023), ("G60", 2024, 2026)],
    "BMW|7 Series":     [("G11 Facelift", 2019, 2022), ("G70", 2023, 2026)],
    "BMW|8 Series":     [("G15", 2019, 2026)],
    "BMW|X1":           [("F48 Facelift", 2020, 2022), ("U11", 2023, 2026)],
    "BMW|X2":           [("F39 Facelift", 2019, 2023), ("U10", 2024, 2026)],
    "BMW|X3":           [("G01 Facelift", 2022, 2024), ("G45", 2025, 2026)],
    "BMW|X4":           [("G02", 2019, 2021), ("G02 LCI", 2022, 2026)],
    "BMW|X5":           [("F15 Facelift", 2018, 2018), ("G05", 2019, 2022), ("G05 LCI", 2023, 2026)],
    "BMW|X6":           [("F16 Facelift", 2018, 2019), ("G06", 2020, 2023), ("G06 LCI", 2024, 2026)],
    "BMW|X7":           [("G07", 2019, 2022), ("G07 LCI", 2023, 2026)],
    "BMW|i3":           [("I01 Facelift", 2018, 2021)],
    "BMW|i4":           [("G26", 2022, 2026)],
    "BMW|i5":           [("G60e", 2024, 2026)],
    "BMW|i7":           [("G70e", 2023, 2026)],
    "BMW|iX":           [("I20", 2022, 2026)],
    "BMW|iX1":          [("U11e", 2023, 2026)],
    "BMW|iX3":          [("G08", 2022, 2024)],
    "BMW|M2":           [("F87 Facelift", 2018, 2021), ("G87", 2023, 2026)],
    "BMW|M3":           [("F80 Facelift", 2018, 2020), ("G80", 2021, 2026)],
    "BMW|M4":           [("G82", 2021, 2026)],
    "BMW|M5":           [("F90", 2018, 2023), ("G90", 2024, 2026)],
    "BMW|M8":           [("G15M", 2019, 2026)],
    "BMW|Z4":           [("G29", 2019, 2026)],

    # ── BUICK ──────────────────────────────────────────────────────────────
    "Buick|Encore":     [("1st Gen Facelift", 2017, 2022)],
    "Buick|Encore GX":  [("1st Gen", 2020, 2026)],
    "Buick|Envision":   [("1st Gen Facelift", 2018, 2020), ("2nd Gen", 2021, 2026)],
    "Buick|Enclave":    [("2nd Gen", 2018, 2022), ("2nd Gen Facelift", 2023, 2026)],
    "Buick|Envista":    [("1st Gen", 2024, 2026)],

    # ── CADILLAC ───────────────────────────────────────────────────────────
    "Cadillac|CT4":     [("1st Gen", 2020, 2026)],
    "Cadillac|CT5":     [("1st Gen", 2020, 2026)],
    "Cadillac|XT4":     [("1st Gen", 2019, 2026)],
    "Cadillac|XT5":     [("2nd Gen", 2017, 2022), ("2nd Gen Facelift", 2023, 2026)],
    "Cadillac|XT6":     [("1st Gen", 2020, 2026)],
    "Cadillac|Escalade":    [("4th Gen", 2015, 2020), ("5th Gen", 2021, 2026)],
    "Cadillac|Escalade ESV":[("4th Gen", 2015, 2020), ("5th Gen", 2021, 2026)],
    "Cadillac|LYRIQ":   [("1st Gen", 2023, 2026)],
    "Cadillac|CELESTIQ":[("1st Gen", 2024, 2026)],
    "Cadillac|OPTIQ":   [("1st Gen", 2025, 2026)],
    "Cadillac|VISTIQ":  [("1st Gen", 2025, 2026)],

    # ── CHEVROLET ──────────────────────────────────────────────────────────
    "Chevrolet|Malibu":     [("9th Gen Facelift", 2016, 2023)],
    "Chevrolet|Camaro":     [("6th Gen Facelift", 2019, 2024)],
    "Chevrolet|Corvette":   [("C7 Facelift", 2018, 2018), ("C8", 2020, 2026)],
    "Chevrolet|Equinox":    [("3rd Gen", 2018, 2021), ("3rd Gen Facelift", 2022, 2024), ("4th Gen", 2025, 2026)],
    "Chevrolet|Equinox EV": [("1st Gen", 2024, 2026)],
    "Chevrolet|Trax":       [("1st Gen Facelift", 2018, 2022), ("2nd Gen", 2024, 2026)],
    "Chevrolet|Trailblazer": [("3rd Gen", 2021, 2026)],
    "Chevrolet|Blazer":     [("5th Gen", 2019, 2026)],
    "Chevrolet|Blazer EV":  [("1st Gen", 2024, 2026)],
    "Chevrolet|Traverse":   [("2nd Gen", 2018, 2021), ("2nd Gen Facelift", 2022, 2024), ("3rd Gen", 2024, 2026)],
    "Chevrolet|Tahoe":      [("4th Gen", 2015, 2020), ("5th Gen", 2021, 2026)],
    "Chevrolet|Suburban":   [("11th Gen", 2015, 2020), ("12th Gen", 2021, 2026)],
    "Chevrolet|Colorado":   [("2nd Gen Facelift", 2017, 2022), ("3rd Gen", 2023, 2026)],
    "Chevrolet|Silverado 1500": [("3rd Gen", 2014, 2018), ("4th Gen", 2019, 2026)],
    "Chevrolet|Silverado EV":   [("1st Gen", 2024, 2026)],
    "Chevrolet|Bolt EV":    [("1st Gen", 2017, 2023)],
    "Chevrolet|Bolt EUV":   [("1st Gen", 2022, 2023)],
    "Chevrolet|Spark":      [("3rd Gen Facelift", 2016, 2022)],
    "Chevrolet|Encore":     [("1st Gen Facelift", 2017, 2022)],
    "Chevrolet|Encore GX":  [("1st Gen", 2020, 2026)],

    # ── CHRYSLER ───────────────────────────────────────────────────────────
    "Chrysler|300":     [("2nd Gen Facelift", 2015, 2023)],
    "Chrysler|Pacifica": [("1st Gen", 2017, 2020), ("1st Gen Facelift", 2021, 2026)],
    "Chrysler|Voyager": [("1st Gen", 2020, 2022)],
    "Chrysler|Airflow": [("1st Gen", 2025, 2026)],

    # ── DODGE ──────────────────────────────────────────────────────────────
    "Dodge|Charger":    [("LD Facelift", 2015, 2023), ("3rd Gen", 2024, 2026)],
    "Dodge|Challenger": [("3rd Gen", 2008, 2023)],  # basically unchanged exterior
    "Dodge|Durango":    [("3rd Gen Facelift", 2018, 2026)],
    "Dodge|Hornet":     [("1st Gen", 2023, 2026)],

    # ── FERRARI ────────────────────────────────────────────────────────────
    "Ferrari|488":          [("488 GTB", 2015, 2019)],
    "Ferrari|F8":           [("F8 Tributo", 2020, 2022)],
    "Ferrari|Roma":         [("1st Gen", 2021, 2026)],
    "Ferrari|Portofino":    [("1st Gen", 2018, 2021)],
    "Ferrari|GTC4Lusso":    [("1st Gen", 2017, 2020)],
    "Ferrari|SF90 Stradale":[("1st Gen", 2021, 2026)],
    "Ferrari|296 GTB":      [("1st Gen", 2022, 2026)],
    "Ferrari|Purosangue":   [("1st Gen", 2023, 2026)],
    "Ferrari|12Cilindri":   [("1st Gen", 2025, 2026)],

    # ── FIAT ───────────────────────────────────────────────────────────────
    "Fiat|500":     [("2nd Gen", 2012, 2020)],
    "Fiat|500X":    [("1st Gen Facelift", 2019, 2022)],
    "Fiat|500L":    [("1st Gen Facelift", 2017, 2020)],
    "Fiat|500e":    [("3rd Gen", 2024, 2026)],
    "Fiat|Panda":   [("4th Gen", 2025, 2026)],

    # ── FORD ───────────────────────────────────────────────────────────────
    "Ford|Mustang":     [("6th Gen Facelift", 2018, 2023), ("7th Gen", 2024, 2026)],
    "Ford|Mustang Mach-E": [("1st Gen", 2021, 2023), ("1st Gen Facelift", 2024, 2026)],
    "Ford|F-150":       [("13th Gen", 2015, 2020), ("14th Gen", 2021, 2026)],
    "Ford|F-150 Lightning": [("1st Gen", 2022, 2025), ("2nd Gen", 2026, 2026)],
    "Ford|Ranger":      [("3rd Gen", 2019, 2023), ("4th Gen", 2024, 2026)],
    "Ford|Maverick":    [("1st Gen", 2022, 2026)],
    "Ford|Explorer":    [("5th Gen Facelift", 2016, 2019), ("6th Gen", 2020, 2026)],
    "Ford|Escape":      [("3rd Gen Facelift", 2017, 2019), ("4th Gen", 2020, 2023), ("4th Gen Facelift", 2024, 2026)],
    "Ford|Edge":        [("2nd Gen Facelift", 2019, 2023)],
    "Ford|Expedition":  [("3rd Gen Facelift", 2018, 2021), ("4th Gen", 2022, 2026)],
    "Ford|Bronco":      [("6th Gen", 2021, 2026)],
    "Ford|Bronco Sport":[("1st Gen", 2021, 2026)],
    "Ford|EcoSport":    [("2nd Gen Facelift", 2018, 2022)],
    "Ford|Fusion":      [("2nd Gen Facelift", 2017, 2020)],

    # ── GENESIS ────────────────────────────────────────────────────────────
    "Genesis|G70":      [("1st Gen", 2019, 2021), ("1st Gen Facelift", 2022, 2026)],
    "Genesis|G80":      [("2nd Gen", 2017, 2020), ("3rd Gen", 2021, 2026)],
    "Genesis|G90":      [("1st Gen Facelift", 2020, 2022), ("2nd Gen", 2023, 2026)],
    "Genesis|GV70":     [("1st Gen", 2022, 2026)],
    "Genesis|GV80":     [("1st Gen", 2021, 2026)],
    "Genesis|GV60":     [("1st Gen", 2023, 2026)],
    "Genesis|G80 Electric": [("1st Gen", 2023, 2026)],
    "Genesis|GV70 Electrified": [("1st Gen", 2023, 2026)],
    "Genesis|GV90":     [("1st Gen", 2026, 2026)],

    # ── GMC ────────────────────────────────────────────────────────────────
    "GMC|Terrain":      [("2nd Gen", 2018, 2021), ("2nd Gen Facelift", 2022, 2026)],
    "GMC|Acadia":       [("2nd Gen", 2017, 2023), ("3rd Gen", 2024, 2026)],
    "GMC|Yukon":        [("4th Gen", 2015, 2020), ("5th Gen", 2021, 2026)],
    "GMC|Yukon XL":     [("4th Gen", 2015, 2020), ("5th Gen", 2021, 2026)],
    "GMC|Sierra 1500":  [("3rd Gen", 2014, 2018), ("4th Gen", 2019, 2026)],
    "GMC|Sierra EV":    [("1st Gen", 2024, 2026)],
    "GMC|Canyon":       [("2nd Gen Facelift", 2017, 2022), ("3rd Gen", 2023, 2026)],
    "GMC|Envoy":        [("1st Gen", 2024, 2026)],
    "GMC|Hummer EV":    [("1st Gen", 2022, 2026)],
    "GMC|Hummer EV SUV":[("1st Gen", 2022, 2026)],

    # ── HONDA ──────────────────────────────────────────────────────────────
    "Honda|Accord":     [("9th Gen", 2018, 2022), ("10th Gen", 2023, 2026)],
    "Honda|Civic":      [("10th Gen", 2016, 2021), ("11th Gen", 2022, 2026)],
    "Honda|Insight":    [("3rd Gen", 2019, 2022)],
    "Honda|CR-V":       [("5th Gen", 2017, 2022), ("6th Gen", 2023, 2026)],
    "Honda|CR-V Hybrid":[("5th Gen Hybrid", 2020, 2022), ("6th Gen Hybrid", 2023, 2026)],
    "Honda|HR-V":       [("2nd Gen", 2016, 2022), ("3rd Gen", 2023, 2026)],
    "Honda|Passport":   [("2nd Gen", 2019, 2022), ("3rd Gen", 2023, 2026)],
    "Honda|Pilot":      [("3rd Gen", 2016, 2022), ("4th Gen", 2023, 2026)],
    "Honda|Ridgeline":  [("2nd Gen", 2017, 2022), ("2nd Gen Facelift", 2023, 2026)],
    "Honda|Odyssey":    [("5th Gen", 2018, 2026)],
    "Honda|Fit":        [("3rd Gen", 2015, 2020)],
    "Honda|Prologue":   [("1st Gen", 2024, 2026)],

    # ── HYUNDAI ────────────────────────────────────────────────────────────
    "Hyundai|Elantra":  [("6th Gen Facelift", 2019, 2020), ("7th Gen", 2021, 2026)],
    "Hyundai|Sonata":   [("8th Gen", 2020, 2026)],
    "Hyundai|Tucson":   [("3rd Gen", 2016, 2021), ("4th Gen", 2022, 2026)],
    "Hyundai|Santa Fe": [("4th Gen", 2019, 2023), ("5th Gen", 2024, 2026)],
    "Hyundai|Palisade": [("1st Gen", 2020, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Hyundai|Venue":    [("1st Gen", 2020, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Hyundai|Kona":     [("1st Gen", 2018, 2023), ("2nd Gen", 2024, 2026)],
    "Hyundai|Kona Electric": [("1st Gen", 2019, 2023), ("2nd Gen", 2024, 2026)],
    "Hyundai|Ioniq":    [("1st Gen", 2017, 2022)],
    "Hyundai|Ioniq 5":  [("1st Gen", 2022, 2026)],
    "Hyundai|Ioniq 6":  [("1st Gen", 2023, 2026)],
    "Hyundai|Ioniq 9":  [("1st Gen", 2026, 2026)],
    "Hyundai|Nexo":     [("1st Gen", 2019, 2026)],
    "Hyundai|Accent":   [("5th Gen", 2018, 2022)],
    "Hyundai|Veloster": [("2nd Gen", 2019, 2021)],
    "Hyundai|Santa Cruz": [("1st Gen", 2022, 2026)],

    # ── INFINITI ───────────────────────────────────────────────────────────
    "Infiniti|Q50":     [("L50 Facelift", 2018, 2026)],
    "Infiniti|Q60":     [("V37", 2017, 2022)],
    "Infiniti|QX50":    [("2nd Gen", 2019, 2026)],
    "Infiniti|QX55":    [("1st Gen", 2022, 2026)],
    "Infiniti|QX60":    [("2nd Gen", 2022, 2026)],
    "Infiniti|QX80":    [("Z62 Facelift", 2018, 2025), ("3rd Gen", 2026, 2026)],

    # ── JAGUAR ─────────────────────────────────────────────────────────────
    "Jaguar|XE":        [("1st Gen Facelift", 2020, 2022)],
    "Jaguar|XF":        [("2nd Gen Facelift", 2020, 2023)],
    "Jaguar|F-Type":    [("1st Gen Facelift", 2018, 2024)],
    "Jaguar|E-Pace":    [("1st Gen Facelift", 2021, 2023)],
    "Jaguar|F-Pace":    [("1st Gen Facelift", 2021, 2024)],
    "Jaguar|I-Pace":    [("1st Gen", 2019, 2023)],
    "Jaguar|Type 00":   [("1st Gen", 2026, 2026)],

    # ── JEEP ───────────────────────────────────────────────────────────────
    "Jeep|Wrangler":        [("JK Facelift", 2018, 2018), ("JL", 2018, 2026)],
    "Jeep|Wrangler 4xe":    [("JL 4xe", 2021, 2026)],
    "Jeep|Grand Cherokee":  [("WK2 Facelift", 2014, 2021), ("WL", 2022, 2026)],
    "Jeep|Grand Cherokee 4xe": [("WL 4xe", 2022, 2026)],
    "Jeep|Cherokee":        [("KL Facelift", 2019, 2023)],
    "Jeep|Compass":         [("MP Facelift", 2021, 2026)],
    "Jeep|Renegade":        [("BU Facelift", 2019, 2026)],
    "Jeep|Gladiator":       [("JT", 2020, 2026)],
    "Jeep|Grand Wagoneer":  [("1st Gen", 2022, 2026)],
    "Jeep|Wagoneer":        [("1st Gen", 2022, 2026)],
    "Jeep|Avenger":         [("1st Gen", 2023, 2026)],
    "Jeep|Recon":           [("1st Gen", 2025, 2026)],

    # ── KIA ────────────────────────────────────────────────────────────────
    "Kia|Forte":        [("3rd Gen", 2019, 2026)],
    "Kia|K5":           [("3rd Gen", 2021, 2026)],
    "Kia|Optima":       [("4th Gen Facelift", 2018, 2020)],
    "Kia|Stinger":      [("1st Gen", 2018, 2023)],
    "Kia|Niro":         [("1st Gen", 2017, 2022), ("2nd Gen", 2023, 2026)],
    "Kia|Niro EV":      [("1st Gen EV", 2019, 2022), ("2nd Gen EV", 2023, 2026)],
    "Kia|Sportage":     [("4th Gen", 2017, 2021), ("5th Gen", 2022, 2026)],
    "Kia|Sorento":      [("3rd Gen Facelift", 2019, 2020), ("4th Gen", 2021, 2026)],
    "Kia|Telluride":    [("1st Gen", 2020, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Kia|Soul":         [("3rd Gen", 2020, 2026)],
    "Kia|Seltos":       [("1st Gen", 2021, 2026)],
    "Kia|EV6":          [("1st Gen", 2022, 2026)],
    "Kia|EV9":          [("1st Gen", 2024, 2026)],
    "Kia|Carnival":     [("3rd Gen", 2022, 2026)],
    "Kia|Sedona":       [("2nd Gen", 2015, 2021)],
    "Kia|Rio":          [("4th Gen", 2018, 2022)],
    "Kia|Cadenza":      [("2nd Gen", 2017, 2020)],

    # ── LAMBORGHINI ────────────────────────────────────────────────────────
    "Lamborghini|Huracan":  [("1st Gen", 2014, 2024)],
    "Lamborghini|Urus":     [("1st Gen", 2019, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Lamborghini|Revuelto": [("1st Gen", 2024, 2026)],
    "Lamborghini|Temerario":[("1st Gen", 2026, 2026)],

    # ── LAND ROVER ─────────────────────────────────────────────────────────
    "Land Rover|Discovery":     [("5th Gen", 2017, 2020), ("5th Gen Facelift", 2021, 2026)],
    "Land Rover|Discovery Sport":[("2nd Gen", 2020, 2026)],
    "Land Rover|Range Rover Sport": [("2nd Gen Facelift", 2018, 2022), ("3rd Gen", 2023, 2026)],
    "Land Rover|Range Rover Velar": [("1st Gen", 2018, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Land Rover|Range Rover Evoque": [("2nd Gen", 2020, 2026)],
    "Land Rover|Range Rover":   [("4th Gen", 2013, 2021), ("5th Gen", 2022, 2026)],
    "Land Rover|Defender":      [("2nd Gen", 2020, 2026)],

    # ── LEXUS ──────────────────────────────────────────────────────────────
    "Lexus|IS":     [("3rd Gen Facelift", 2021, 2026)],
    "Lexus|ES":     [("7th Gen", 2019, 2026)],
    "Lexus|LS":     [("5th Gen Facelift", 2021, 2026)],
    "Lexus|UX":     [("1st Gen", 2019, 2026)],
    "Lexus|NX":     [("2nd Gen", 2022, 2026)],
    "Lexus|RX":     [("4th Gen", 2016, 2022), ("5th Gen", 2023, 2026)],
    "Lexus|GX":     [("2nd Gen Facelift", 2020, 2023), ("3rd Gen", 2024, 2026)],
    "Lexus|LX":     [("3rd Gen Facelift", 2016, 2021), ("4th Gen", 2022, 2026)],
    "Lexus|LC":     [("1st Gen", 2018, 2026)],
    "Lexus|RC":     [("1st Gen Facelift", 2019, 2024)],
    "Lexus|RZ":     [("1st Gen", 2023, 2026)],
    "Lexus|TX":     [("1st Gen", 2024, 2026)],
    "Lexus|GX 550": [("3rd Gen", 2024, 2026)],

    # ── LINCOLN ────────────────────────────────────────────────────────────
    "Lincoln|MKZ":      [("2nd Gen Facelift", 2017, 2020)],
    "Lincoln|Continental": [("10th Gen", 2017, 2019)],
    "Lincoln|Corsair":  [("1st Gen", 2020, 2023), ("1st Gen Facelift", 2024, 2026)],
    "Lincoln|Nautilus": [("1st Gen", 2019, 2023), ("2nd Gen", 2024, 2026)],
    "Lincoln|Aviator":  [("2nd Gen", 2020, 2026)],
    "Lincoln|Navigator":[("4th Gen", 2018, 2021), ("4th Gen Facelift", 2022, 2026)],

    # ── MASERATI ───────────────────────────────────────────────────────────
    "Maserati|Ghibli":      [("3rd Gen Facelift", 2018, 2023)],
    "Maserati|Quattroporte":[("6th Gen Facelift", 2017, 2023)],
    "Maserati|Levante":     [("1st Gen Facelift", 2019, 2023)],
    "Maserati|Grecale":     [("1st Gen", 2023, 2026)],
    "Maserati|GranTurismo": [("2nd Gen", 2023, 2026)],
    "Maserati|MC20":        [("1st Gen", 2022, 2026)],

    # ── MAZDA ──────────────────────────────────────────────────────────────
    "Mazda|Mazda3":     [("4th Gen", 2019, 2026)],
    "Mazda|Mazda6":     [("3rd Gen Facelift", 2018, 2021)],
    "Mazda|CX-3":       [("1st Gen Facelift", 2018, 2021)],
    "Mazda|CX-30":      [("1st Gen", 2020, 2026)],
    "Mazda|CX-5":       [("2nd Gen", 2017, 2021), ("2nd Gen Facelift", 2022, 2026)],
    "Mazda|CX-50":      [("1st Gen", 2023, 2026)],
    "Mazda|CX-9":       [("2nd Gen Facelift", 2018, 2023)],
    "Mazda|CX-90":      [("1st Gen", 2024, 2026)],
    "Mazda|MX-5 Miata": [("4th Gen Facelift", 2019, 2026)],
    "Mazda|MX-30":      [("1st Gen", 2022, 2025)],

    # ── MERCEDES-BENZ ──────────────────────────────────────────────────────
    "Mercedes-Benz|A-Class":    [("4th Gen", 2019, 2023)],
    "Mercedes-Benz|C-Class":    [("W205 Facelift", 2019, 2021), ("W206", 2022, 2026)],
    "Mercedes-Benz|E-Class":    [("W213 Facelift", 2021, 2023), ("W214", 2024, 2026)],
    "Mercedes-Benz|S-Class":    [("W222 Facelift", 2018, 2020), ("W223", 2021, 2026)],
    "Mercedes-Benz|CLA":        [("C117 Facelift", 2017, 2019), ("C118", 2020, 2026)],
    "Mercedes-Benz|CLS":        [("C257", 2019, 2023)],
    "Mercedes-Benz|GLA":        [("H247", 2021, 2026)],
    "Mercedes-Benz|GLB":        [("X247", 2020, 2026)],
    "Mercedes-Benz|GLC":        [("X253 Facelift", 2020, 2022), ("X254", 2023, 2026)],
    "Mercedes-Benz|GLE":        [("W166 Facelift", 2018, 2019), ("V167", 2020, 2026)],
    "Mercedes-Benz|GLS":        [("X166 Facelift", 2017, 2019), ("X167", 2020, 2026)],
    "Mercedes-Benz|G-Class":    [("W463A", 2019, 2026)],
    "Mercedes-Benz|EQB":        [("X243", 2022, 2026)],
    "Mercedes-Benz|EQE":        [("V295", 2023, 2026)],
    "Mercedes-Benz|EQE SUV":    [("X294", 2023, 2026)],
    "Mercedes-Benz|EQS":        [("V297", 2022, 2026)],
    "Mercedes-Benz|EQS SUV":    [("X296", 2023, 2026)],
    "Mercedes-Benz|AMG GT":     [("C190 Facelift", 2018, 2023), ("C192", 2024, 2026)],
    "Mercedes-Benz|SL":         [("R232", 2022, 2026)],
    "Mercedes-Benz|Sprinter":   [("3rd Gen", 2019, 2026)],

    # ── MINI ───────────────────────────────────────────────────────────────
    "MINI|Hardtop":     [("F56 Facelift", 2018, 2021), ("F66", 2024, 2026)],
    "MINI|Convertible": [("F57 Facelift", 2019, 2023)],
    "MINI|Clubman":     [("F54 Facelift", 2020, 2024)],
    "MINI|Countryman":  [("F60 Facelift", 2018, 2023), ("U25", 2024, 2026)],
    "MINI|Cooper SE":   [("F56 Electric", 2020, 2023)],
    "MINI|Aceman":      [("1st Gen", 2025, 2026)],
    "MINI|John Cooper Works": [("F56 JCW Facelift", 2018, 2023), ("F66 JCW", 2024, 2026)],

    # ── MITSUBISHI ─────────────────────────────────────────────────────────
    "Mitsubishi|Outlander":     [("3rd Gen Facelift", 2018, 2021), ("4th Gen", 2022, 2026)],
    "Mitsubishi|Outlander PHEV":[("3rd Gen PHEV", 2018, 2021), ("4th Gen PHEV", 2022, 2026)],
    "Mitsubishi|Eclipse Cross": [("1st Gen", 2018, 2021), ("1st Gen Facelift", 2022, 2026)],
    "Mitsubishi|Mirage":        [("1st Gen Facelift", 2017, 2026)],
    "Mitsubishi|Outlander Sport":[("1st Gen Facelift", 2016, 2024)],

    # ── NISSAN ─────────────────────────────────────────────────────────────
    "Nissan|Altima":    [("5th Gen Facelift", 2018, 2018), ("6th Gen", 2019, 2026)],
    "Nissan|Sentra":    [("7th Gen", 2020, 2026)],
    "Nissan|Maxima":    [("8th Gen Facelift", 2018, 2023)],
    "Nissan|Versa":     [("2nd Gen Facelift", 2018, 2019), ("3rd Gen", 2020, 2026)],
    "Nissan|Rogue":     [("2nd Gen Facelift", 2018, 2020), ("3rd Gen", 2021, 2026)],
    "Nissan|Rogue Sport":   [("1st Gen Facelift", 2018, 2022)],
    "Nissan|Murano":    [("3rd Gen Facelift", 2019, 2025), ("4th Gen", 2026, 2026)],
    "Nissan|Pathfinder":[("4th Gen Facelift", 2017, 2021), ("5th Gen", 2022, 2026)],
    "Nissan|Armada":    [("2nd Gen Facelift", 2021, 2026)],
    "Nissan|Kicks":     [("1st Gen", 2018, 2021), ("2nd Gen", 2022, 2026)],
    "Nissan|Frontier":  [("2nd Gen Facelift", 2020, 2021), ("3rd Gen", 2022, 2026)],
    "Nissan|Titan":     [("2nd Gen Facelift", 2020, 2026)],
    "Nissan|Leaf":      [("2nd Gen", 2018, 2026)],
    "Nissan|Ariya":     [("1st Gen", 2023, 2026)],
    "Nissan|Z":         [("RZ34", 2023, 2026)],
    "Nissan|370Z":      [("Z34 Facelift", 2018, 2021)],

    # ── PORSCHE ────────────────────────────────────────────────────────────
    "Porsche|Macan":            [("95B Facelift", 2019, 2023), ("J1 Electric", 2024, 2026)],
    "Porsche|Macan Electric":   [("J1", 2024, 2026)],
    "Porsche|Cayenne":          [("9YB", 2019, 2023), ("9YB Facelift", 2024, 2026)],
    "Porsche|Cayenne Coupe":    [("9YB Coupe", 2020, 2023), ("9YB Coupe Facelift", 2024, 2026)],
    "Porsche|Taycan":           [("J1", 2020, 2024), ("J1 Facelift", 2025, 2026)],
    "Porsche|Taycan Cross Turismo": [("J1 CT", 2021, 2024), ("J1 CT Facelift", 2025, 2026)],
    "Porsche|Taycan Sport Turismo": [("J1 ST", 2022, 2024), ("J1 ST Facelift", 2025, 2026)],
    "Porsche|911":          [("992", 2020, 2026)],
    "Porsche|718 Cayman":   [("982 Facelift", 2020, 2026)],
    "Porsche|718 Boxster":  [("982 Facelift", 2020, 2026)],
    "Porsche|Panamera":     [("971 Facelift", 2021, 2026)],

    # ── RAM ────────────────────────────────────────────────────────────────
    "Ram|1500":         [("4th Gen Classic", 2018, 2018), ("5th Gen DT", 2019, 2026)],
    "Ram|1500 REV":     [("1st Gen", 2024, 2026)],

    # ── RIVIAN ─────────────────────────────────────────────────────────────
    "Rivian|R1T":   [("1st Gen", 2022, 2024), ("1st Gen Facelift", 2025, 2026)],
    "Rivian|R1S":   [("1st Gen", 2022, 2024), ("1st Gen Facelift", 2025, 2026)],
    "Rivian|R2":    [("1st Gen", 2026, 2026)],

    # ── ROLLS-ROYCE ────────────────────────────────────────────────────────
    "Rolls-Royce|Ghost":    [("6th Gen", 2021, 2026)],
    "Rolls-Royce|Phantom":  [("8th Gen", 2018, 2026)],
    "Rolls-Royce|Wraith":   [("2nd Gen", 2013, 2023)],
    "Rolls-Royce|Dawn":     [("2nd Gen", 2016, 2022)],
    "Rolls-Royce|Cullinan": [("1st Gen", 2019, 2026)],
    "Rolls-Royce|Spectre":  [("1st Gen", 2024, 2026)],
    "Rolls-Royce|Black Badge Ghost": [("6th Gen BB", 2021, 2026)],

    # ── SUBARU ─────────────────────────────────────────────────────────────
    "Subaru|Impreza":   [("5th Gen", 2017, 2023), ("6th Gen", 2024, 2026)],
    "Subaru|Legacy":    [("6th Gen", 2020, 2026)],
    "Subaru|Outback":   [("5th Gen Facelift", 2018, 2019), ("6th Gen", 2020, 2026)],
    "Subaru|Forester":  [("5th Gen", 2019, 2026)],
    "Subaru|Crosstrek": [("2nd Gen", 2018, 2023), ("3rd Gen", 2024, 2026)],
    "Subaru|Ascent":    [("1st Gen", 2019, 2026)],
    "Subaru|BRZ":       [("1st Gen", 2013, 2021), ("2nd Gen", 2022, 2026)],
    "Subaru|WRX":       [("4th Gen", 2015, 2021), ("5th Gen", 2022, 2026)],
    "Subaru|Solterra":  [("1st Gen", 2023, 2026)],

    # ── TESLA ──────────────────────────────────────────────────────────────
    "Tesla|Model 3":    [("1st Gen", 2018, 2023), ("Highland", 2024, 2026)],
    "Tesla|Model S":    [("1st Gen Facelift", 2016, 2020), ("Plaid", 2021, 2026)],
    "Tesla|Model X":    [("1st Gen Facelift", 2016, 2020), ("Plaid", 2021, 2026)],
    "Tesla|Model Y":    [("1st Gen", 2020, 2024), ("Juniper", 2025, 2026)],
    "Tesla|Cybertruck": [("1st Gen", 2024, 2026)],
    "Tesla|Roadster":   [("2nd Gen", 2025, 2026)],

    # ── TOYOTA ─────────────────────────────────────────────────────────────
    "Toyota|Camry":     [("8th Gen", 2018, 2024), ("9th Gen", 2025, 2026)],
    "Toyota|Corolla":   [("11th Gen Facelift", 2017, 2018), ("12th Gen", 2019, 2026)],
    "Toyota|Avalon":    [("4th Gen Facelift", 2018, 2018), ("5th Gen", 2019, 2022)],
    "Toyota|Prius":     [("4th Gen Facelift", 2019, 2022), ("5th Gen", 2023, 2026)],
    "Toyota|RAV4":      [("4th Gen", 2018, 2018), ("5th Gen", 2019, 2026)],
    "Toyota|RAV4 Hybrid":   [("5th Gen Hybrid", 2019, 2026)],
    "Toyota|RAV4 Prime":    [("5th Gen Prime", 2021, 2026)],
    "Toyota|Highlander":    [("3rd Gen", 2018, 2019), ("4th Gen", 2020, 2026)],
    "Toyota|4Runner":       [("5th Gen Facelift", 2018, 2024), ("6th Gen", 2025, 2026)],
    "Toyota|Sequoia":       [("2nd Gen Facelift", 2018, 2021), ("3rd Gen", 2022, 2026)],
    "Toyota|Land Cruiser":  [("4th Gen", 2022, 2026)],
    "Toyota|Venza":         [("2nd Gen", 2021, 2026)],
    "Toyota|Crown":         [("16th Gen", 2023, 2026)],
    "Toyota|bZ4X":          [("1st Gen", 2023, 2026)],
    "Toyota|Tacoma":        [("3rd Gen Facelift", 2018, 2023), ("4th Gen", 2024, 2026)],
    "Toyota|Tundra":        [("2nd Gen Facelift", 2018, 2021), ("3rd Gen", 2022, 2026)],
    "Toyota|Sienna":        [("3rd Gen Facelift", 2018, 2020), ("4th Gen", 2021, 2026)],
    "Toyota|86":            [("1st Gen Facelift", 2017, 2021)],
    "Toyota|GR86":          [("2nd Gen", 2022, 2026)],
    "Toyota|Supra":         [("5th Gen", 2020, 2026)],
    "Toyota|C-HR":          [("1st Gen Facelift", 2018, 2022)],
    "Toyota|Corolla Cross": [("1st Gen", 2022, 2026)],

    # ── VOLKSWAGEN ─────────────────────────────────────────────────────────
    "Volkswagen|Jetta":     [("6th Gen Facelift", 2015, 2018), ("7th Gen", 2019, 2026)],
    "Volkswagen|Passat":    [("7th Gen Facelift", 2020, 2022)],
    "Volkswagen|Arteon":    [("1st Gen", 2019, 2023)],
    "Volkswagen|Golf":      [("7th Gen Facelift", 2018, 2021)],
    "Volkswagen|Golf GTI":  [("7th Gen Facelift", 2018, 2021), ("8th Gen", 2022, 2026)],
    "Volkswagen|Golf R":    [("7th Gen Facelift", 2018, 2019), ("8th Gen", 2022, 2026)],
    "Volkswagen|Tiguan":    [("2nd Gen", 2018, 2023), ("3rd Gen", 2024, 2026)],
    "Volkswagen|Atlas":     [("1st Gen", 2018, 2020), ("1st Gen Facelift", 2021, 2026)],
    "Volkswagen|Atlas Cross Sport": [("1st Gen", 2020, 2022), ("1st Gen Facelift", 2022, 2026)],
    "Volkswagen|ID.4":      [("1st Gen", 2021, 2026)],
    "Volkswagen|ID.Buzz":   [("1st Gen", 2024, 2026)],
    "Volkswagen|Taos":      [("1st Gen", 2022, 2026)],

    # ── VOLVO ──────────────────────────────────────────────────────────────
    "Volvo|S60":    [("3rd Gen", 2019, 2026)],
    "Volvo|S90":    [("2nd Gen Facelift", 2021, 2026)],
    "Volvo|V60":    [("2nd Gen", 2019, 2026)],
    "Volvo|V90":    [("2nd Gen Facelift", 2017, 2026)],
    "Volvo|XC40":   [("1st Gen", 2019, 2022), ("1st Gen Facelift", 2023, 2026)],
    "Volvo|XC40 Recharge": [("1st Gen EV", 2021, 2026)],
    "Volvo|XC60":   [("2nd Gen", 2018, 2022), ("2nd Gen Facelift", 2023, 2026)],
    "Volvo|XC90":   [("2nd Gen", 2016, 2022), ("2nd Gen Facelift", 2023, 2026)],
    "Volvo|EX30":   [("1st Gen", 2024, 2026)],
    "Volvo|EX90":   [("1st Gen", 2025, 2026)],
    "Volvo|C40 Recharge": [("1st Gen", 2022, 2026)],
}


# ─────────────────────────────────────────────────────────────────────────────
# BUILD OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

def build():
    with open(CARS_PATH) as f:
        cars_data = json.load(f)
    all_vehicles = cars_data["vehicles"]

    # Index vehicles by make+model+year for fast lookup
    vehicle_index = {}
    for v in all_vehicles:
        vehicle_index[(v["make"], v["model"], v["year"])] = v

    # Build the full generations lookup: (make, model, year) -> gen info
    gen_lookup = {}   # (make, model, year) -> {gen_name, gen_start, gen_end, photo_year}
    missing_gen = []  # vehicles in cars.json with no generation data

    for v in all_vehicles:
        key_str = f"{v['make']}|{v['model']}"
        year = v["year"]
        make = v["make"]
        model = v["model"]

        if key_str not in GENERATIONS:
            missing_gen.append((make, model, year))
            # Default: treat each year as its own generation
            gen_lookup[(make, model, year)] = {
                "gen_name": "Unknown",
                "gen_start": year,
                "gen_end": year,
                "photo_year": year,
                "needs_photo": True,
            }
            continue

        gens = GENERATIONS[key_str]
        matched = False
        for gen_name, start, end in gens:
            if start <= year <= end:
                # Clamp photo_year to the first year this model appears in our dataset.
                # If the generation started before 2018 (our dataset start), the
                # representative photo year becomes the first dataset year (e.g. 2018).
                years_in_dataset_for_gen = sorted(
                    v2["year"] for v2 in all_vehicles
                    if v2["make"] == make and v2["model"] == model
                    and start <= v2["year"] <= end
                )
                photo_year = years_in_dataset_for_gen[0] if years_in_dataset_for_gen else start
                gen_lookup[(make, model, year)] = {
                    "gen_name": gen_name,
                    "gen_start": start,
                    "gen_end": end,
                    "photo_year": photo_year,
                    "needs_photo": year == photo_year,  # only the representative year needs a photo
                }
                matched = True
                break

        if not matched:
            # Year outside all defined generation ranges — treat as standalone
            gen_lookup[(make, model, year)] = {
                "gen_name": "Unlisted Year",
                "gen_start": year,
                "gen_end": year,
                "photo_year": year,
                "needs_photo": True,
            }

    # Build structured generations.json output
    by_model = {}
    for (make, model, year), info in sorted(gen_lookup.items()):
        key = f"{make}|{model}"
        if key not in by_model:
            by_model[key] = {"make": make, "model": model, "generations": {}}
        gen_name = info["gen_name"]
        if gen_name not in by_model[key]["generations"]:
            by_model[key]["generations"][gen_name] = {
                "gen_name": gen_name,
                "years": [],
                "photo_year": info["photo_year"],
            }
        by_model[key]["generations"][gen_name]["years"].append(year)

    # Sort years within each generation
    models_list = []
    for key, data in sorted(by_model.items()):
        gens_out = []
        for gen_name, gen_data in data["generations"].items():
            gens_out.append({
                "gen_name": gen_data["gen_name"],
                "year_start": min(gen_data["years"]),
                "year_end": max(gen_data["years"]),
                "photo_year": gen_data["photo_year"],
                "years_in_dataset": sorted(gen_data["years"]),
            })
        gens_out.sort(key=lambda g: g["year_start"])
        models_list.append({
            "make": data["make"],
            "model": data["model"],
            "generations": gens_out,
        })

    gen_output = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "description": "Generation/refresh reference for all make+model combos 2018-2026. photo_year = the representative model year for that generation's photo.",
            "total_models": len(models_list),
            "coverage_note": f"{len(missing_gen)} vehicle-years had no generation data and defaulted to year-by-year.",
        },
        "models": models_list,
    }

    GEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GEN_PATH, "w") as f:
        json.dump(gen_output, f, indent=2)

    # ── photo_needed.json ─────────────────────────────────────────────────
    # One entry per generation — the representative year that needs a photo
    photo_needed = []
    seen_photos = set()

    for (make, model, year), info in sorted(gen_lookup.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        if not info["needs_photo"]:
            continue
        photo_key = (make, model, info["photo_year"])
        if photo_key in seen_photos:
            continue
        seen_photos.add(photo_key)

        v = vehicle_index.get((make, model, year), {})
        photo_needed.append({
            "year": info["photo_year"],
            "make": make,
            "model": model,
            "body_type": v.get("body_type", ""),
            "gen_name": info["gen_name"],
            "gen_year_range": f"{info['gen_start']}–{info['gen_end']}",
            "photo_filename": f"photos/{make}/{info['photo_year']}_{model.replace(' ', '_').replace('/', '-')}.jpg",
            "has_local_photo": False,  # update at runtime
        })

    photo_output = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "description": "One entry per generation per model — the only years that need a unique photo. Same generation = same photo used across all years.",
            "total_photos_needed": len(photo_needed),
            "vs_naive_per_year": len(all_vehicles),
            "photos_saved": len(all_vehicles) - len(photo_needed),
        },
        "photos": photo_needed,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(photo_output, f, indent=2)

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"✅ Generations reference: {GEN_PATH}")
    print(f"   {len(models_list)} make/model combos covered")
    total_gens = sum(len(m["generations"]) for m in models_list)
    print(f"   {total_gens} total generations/refreshes defined")
    print()
    print(f"✅ Photo needed list: {OUT_PATH}")
    print(f"   {len(photo_needed)} unique photos needed")
    print(f"   {len(all_vehicles)} total vehicle-years in database")
    print(f"   {len(all_vehicles) - len(photo_needed)} redundant photos avoided ({(len(all_vehicles) - len(photo_needed)) / len(all_vehicles) * 100:.0f}% reduction)")

    if missing_gen:
        unique_missing = sorted(set((m, mo) for m, mo, _ in missing_gen))
        print(f"\n⚠  {len(unique_missing)} models missing from generations data:")
        for make, model in unique_missing[:20]:
            print(f"     {make} {model}")
        if len(unique_missing) > 20:
            print(f"     ...and {len(unique_missing)-20} more")

    # Body type breakdown of photos needed
    by_type = {}
    for p in photo_needed:
        by_type.setdefault(p["body_type"] or "Unknown", 0)
        by_type[p["body_type"] or "Unknown"] += 1
    print(f"\n   Photos needed by body type:")
    for bt, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"     {bt:20s} {count}")


if __name__ == "__main__":
    build()
