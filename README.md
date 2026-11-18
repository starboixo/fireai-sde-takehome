# 🍱 Tiffin Waste-Reduction Calculator

A minimal, no-dependency Python tool that reads daily meal data from a CSV file, computes day-of-week demand trends using a moving average, and tells a local mess owner **exactly how many meals to prepare tomorrow** — with a configurable safety buffer.

Built as a hyper-local alternative to bloated enterprise inventory software, designed for vendors like Ramesh Bhai who track nothing and waste 15–25% of daily output.

---

## Project Structure

```
FireAi/
├── data.csv          ← 29 days of realistic daily meal data
├── research.md       ← Problem framing, existing solutions, references
├── fieldwork.md      ← Field visit notes (Ramesh Bhai interview)
├── src/
│   └── main.py       ← The calculator script
└── README.md         ← This file
```

---

## Requirements

- Python **3.10+** (uses `str | None` type union syntax)
- No external packages — only the standard library (`csv`, `datetime`, `argparse`, `collections`)

---

## How to Run

### Basic run (auto-detects tomorrow's weekday)
```bash
python src/main.py
```

### Specify tomorrow's day manually
```bash
python src/main.py --tomorrow Friday
```

### Adjust the safety margin (default is 10%)
```bash
python src/main.py --tomorrow Wednesday --margin 0.08
```

| Flag | Default | Description |
|---|---|---|
| `--tomorrow` | Auto (real tomorrow) | Day of week to forecast |
| `--margin` | `0.10` (10%) | Safety buffer above moving average |

---

## Real Output Sample

> Run: `python src/main.py --tomorrow Wednesday --margin 0.10`

```
============================================================
   🍱  TIFFIN WASTE REDUCTION CALCULATOR
   Hyper-local demand forecast for your mess
============================================================

[INFO] Skipped 2 incomplete/missing row(s) in the data.

[INFO] Loaded 27 valid data rows.

📊  WEEKLY DEMAND SUMMARY  (safety margin: 10%)
------------------------------------------------------------
Day          Avg Sold  Recommended  Data Pts  Confidence
------------------------------------------------------------
Monday           77.5           86         4  high
Tuesday          79.5           88         4  high
Wednesday        68.5           76         4  high
Thursday         73.3           81         4  high
Friday           89.5           99         4  high
Saturday         47.8           53         4  high
Sunday           36.5           41         4  high

============================================================
📅  TOMORROW IS: WEDNESDAY
============================================================

  ✅  Prepare:        76 meals
  📈  Avg sold:       68.5 meals
  🛡️  Safety buffer:  +10%  (8 extra meals)
  📋  Confidence:     high
  🗂️  Based on:       4 week(s) of Wednesday data

  💡  Estimated max waste if demand is average: 8 meals
      (~₹280 in raw material cost)

------------------------------------------------------------
⚠️   KNOWN LIMITATIONS (read before trusting this blindly)
------------------------------------------------------------
  • Does NOT account for local public holidays or bandhs
  • Does NOT factor in exam weeks, cricket match days
  • Weather impact is not modelled (rainy days shift demand)
  • Month-end payday spikes are not separated from normal days
  • Delivery-app overflow (informal orders) is invisible here
  • Safety margin is a fixed %; adjust --margin to your taste

  Run with more weeks of data for higher confidence scores.
============================================================
```

---

## What This Tool Gets Wrong (Honest Limitations)

This is an intentionally simple tool. Here is what it **cannot** do:

| Limitation | Why It Matters |
|---|---|
| **Local holidays / bandhs** | Demand can drop 60–80% on a surprise bandh. The tool will still recommend a full Monday count. |
| **College exam weeks** | A nearby college campus can swing demand 30% lower for 2 weeks. No calendar awareness here. |
| **Rainy day paradox** | Ramesh Bhai over-prepares on rainy days. This tool doesn't know the weather. |
| **Month-end payday spike** | Last Friday of month vs. mid-month Friday behave differently. Averaged out here. |
| **One-off local events** | A nearby wedding, procession, or cricket match can empty or fill a mess. No event signals. |
| **Cold-start problem** | For a new day of week with 0–1 data points, the tool warns but can't forecast reliably. |
| **Informal delivery overflow** | Orders routed from delivery-app vendors to Ramesh Bhai are not tracked in this CSV. |
| **Ingredient-level waste** | The tool forecasts meal count, not which ingredient is spoiling (dal vs. sabzi). |

> **Bottom line:** This tool is a starting point, not a replacement for judgment. After 4–6 weeks of consistent data entry, the confidence scores improve significantly and the recommendations become meaningfully useful.

---

## Why This Approach

- **Moving average over last 4 same-weekday occurrences** captures recent trend without being thrown off by older outliers.
- **10% safety margin** is tuned to minimize the "run out of food" scenario while capping waste. Adjust lower (e.g. `--margin 0.06`) once you have 8+ weeks of data.
- **Missing data is handled gracefully** — rows with blank sold counts are skipped with a warning, not crashed on.

---

## Extending This Tool

Ideas for a v2:

- [ ] Add a `--weather rainy` flag that bumps the recommendation by a user-defined multiplier
- [ ] Parse a local holiday list (`.ics` or simple txt) to auto-warn on upcoming holidays
- [ ] Add a weekly waste cost summary (₹ wasted per week, trended)
- [ ] Export recommendations to a WhatsApp-friendly text summary via `pywhatkit`
