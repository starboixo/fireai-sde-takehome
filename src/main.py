"""
Hyper-Local Tiffin Waste-Reduction Calculator
----------------------------------------------
Reads daily meal production data from data.csv, analyzes day-of-week demand
trends using moving averages and a configurable safety margin, and outputs a
concrete recommendation for tomorrow's meal preparation count.

Usage:
    python src/main.py
    python src/main.py --tomorrow Friday
    python src/main.py --margin 0.08
"""

import csv
import sys
import os
import argparse
from datetime import datetime, timedelta
from collections import defaultdict


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data.csv")
DEFAULT_SAFETY_MARGIN = 0.10   # 10% buffer above moving average
MIN_DATA_POINTS = 2            # minimum rows needed per day to trust the average
MOVING_AVERAGE_WINDOW = 4      # last N occurrences of a weekday to average over


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
def load_data(filepath: str) -> list[dict]:
    """
    Load and parse data.csv. Skips rows with missing MealsSold values.
    Returns a list of dicts with typed fields.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] Data file not found: {filepath}")
        print("        Please make sure 'data.csv' exists in the project root.")
        sys.exit(1)

    records = []
    skipped = 0

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 = header
            date_str = row.get("Date", "").strip()
            dow      = row.get("DayOfWeek", "").strip()
            sold_str = row.get("MealsSold", "").strip()
            prep_str = row.get("MealsPrepared", "").strip()

            # Skip rows with no sales data
            if not sold_str or not prep_str:
                skipped += 1
                continue

            try:
                records.append({
                    "date":     date_str,
                    "dow":      dow,
                    "prepared": int(prep_str),
                    "sold":     int(sold_str),
                })
            except ValueError:
                skipped += 1   # non-numeric noise — skip silently

    if skipped:
        print(f"[INFO] Skipped {skipped} incomplete/missing row(s) in the data.\n")

    if not records:
        print("[ERROR] No valid data rows found in data.csv.")
        sys.exit(1)

    return records


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def group_by_weekday(records: list[dict]) -> dict[str, list[int]]:
    """
    Groups MealsSold values by DayOfWeek string.
    Returns e.g. {"Monday": [74, 77, 75, 78], "Tuesday": [79, 80, 81], ...}
    """
    groups: dict[str, list[int]] = defaultdict(list)
    for r in records:
        if r["dow"]:
            groups[r["dow"]].append(r["sold"])
    return dict(groups)


def moving_average(values: list[int], window: int) -> float:
    """Return the simple moving average of the last `window` values."""
    tail = values[-window:]
    return sum(tail) / len(tail)


def compute_recommendations(
    groups: dict[str, list[int]],
    safety_margin: float,
    window: int,
    min_points: int,
) -> dict[str, dict]:
    """
    For each weekday with enough data, compute:
      - moving_avg  : average meals sold (last N weeks)
      - recommended : moving_avg × (1 + safety_margin), rounded up
      - confidence  : 'high' / 'medium' / 'low' based on data points
    """
    results = {}
    for day, sold_list in groups.items():
        n = len(sold_list)
        avg = moving_average(sold_list, window)
        recommended = int(avg * (1 + safety_margin)) + 1  # ceil-style buffer

        if n >= 4:
            confidence = "high"
        elif n >= MIN_DATA_POINTS:
            confidence = "medium"
        else:
            confidence = "low  ⚠️  (only 1 data point — treat with caution)"

        results[day] = {
            "data_points":   n,
            "avg_sold":      round(avg, 1),
            "recommended":   recommended,
            "confidence":    confidence,
        }
    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def print_banner():
    print("=" * 60)
    print("   🍱  TIFFIN WASTE REDUCTION CALCULATOR")
    print("   Hyper-local demand forecast for your mess")
    print("=" * 60)
    print()


def print_weekly_summary(recommendations: dict[str, dict], safety_margin: float):
    print(f"📊  WEEKLY DEMAND SUMMARY  (safety margin: {int(safety_margin*100)}%)")
    print("-" * 60)
    header = f"{'Day':<12} {'Avg Sold':>9} {'Recommended':>12} {'Data Pts':>9}  Confidence"
    print(header)
    print("-" * 60)

    for day in WEEKDAY_ORDER:
        if day not in recommendations:
            print(f"{day:<12} {'—':>9} {'—':>12} {'—':>9}  no data")
            continue
        r = recommendations[day]
        print(
            f"{day:<12} {r['avg_sold']:>9} {r['recommended']:>12} {r['data_points']:>9}  {r['confidence']}"
        )
    print()


def print_tomorrow_recommendation(
    tomorrow_dow: str,
    recommendations: dict[str, dict],
    safety_margin: float,
):
    print("=" * 60)
    print(f"📅  TOMORROW IS: {tomorrow_dow.upper()}")
    print("=" * 60)

    if tomorrow_dow not in recommendations:
        print(f"[WARNING] No historical data for {tomorrow_dow}.")
        print("          Cannot make a reliable recommendation.")
        print("          Consider tracking this day manually for 2–3 weeks.")
        return

    r = recommendations[tomorrow_dow]
    print(f"\n  ✅  Prepare:        {r['recommended']} meals")
    print(f"  📈  Avg sold:       {r['avg_sold']} meals")
    print(f"  🛡️  Safety buffer:  +{int(safety_margin * 100)}%  ({r['recommended'] - round(r['avg_sold'])} extra meals)")
    print(f"  📋  Confidence:     {r['confidence']}")
    print(f"  🗂️  Based on:       {r['data_points']} week(s) of {tomorrow_dow} data\n")

    # Waste estimate
    estimated_waste = r["recommended"] - round(r["avg_sold"])
    cost_per_meal   = 35  # rough raw-material cost in ₹
    print(f"  💡  Estimated max waste if demand is average: {estimated_waste} meals")
    print(f"      (~₹{estimated_waste * cost_per_meal} in raw material cost)")
    print()


def print_caveats():
    print("-" * 60)
    print("⚠️   KNOWN LIMITATIONS (read before trusting this blindly)")
    print("-" * 60)
    print("  • Does NOT account for local public holidays or bandhs")
    print("  • Does NOT factor in exam weeks, cricket match days")
    print("  • Weather impact is not modelled (rainy days shift demand)")
    print("  • Month-end payday spikes are not separated from normal days")
    print("  • Delivery-app overflow (informal orders) is invisible here")
    print("  • Safety margin is a fixed %; adjust --margin to your taste")
    print()
    print("  Run with more weeks of data for higher confidence scores.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Tiffin Waste Reduction Calculator — daily prep recommendation"
    )
    parser.add_argument(
        "--tomorrow",
        type=str,
        default=None,
        help="Day of week for tomorrow (e.g. 'Friday'). Defaults to actual tomorrow.",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=DEFAULT_SAFETY_MARGIN,
        help=f"Safety margin as a decimal (default: {DEFAULT_SAFETY_MARGIN} = 10%%).",
    )
    return parser.parse_args()


def get_tomorrow_dow(override: str | None) -> str:
    if override:
        # Capitalise first letter for consistency
        return override.strip().capitalize()
    tomorrow = datetime.today() + timedelta(days=1)
    return tomorrow.strftime("%A")  # e.g. "Tuesday"


def main():
    args = parse_args()

    print_banner()

    # 1. Load data
    records = load_data(DATA_FILE)
    print(f"[INFO] Loaded {len(records)} valid data rows.\n")

    # 2. Group and analyse
    groups          = group_by_weekday(records)
    recommendations = compute_recommendations(
        groups, args.margin, MOVING_AVERAGE_WINDOW, MIN_DATA_POINTS
    )

    # 3. Print weekly summary table
    print_weekly_summary(recommendations, args.margin)

    # 4. Tomorrow's recommendation
    tomorrow_dow = get_tomorrow_dow(args.tomorrow)
    print_tomorrow_recommendation(tomorrow_dow, recommendations, args.margin)

    # 5. Caveats
    print_caveats()


if __name__ == "__main__":
    main()
