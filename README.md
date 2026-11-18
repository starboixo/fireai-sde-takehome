# Tiffin Waste-Reduction Calculator

A minimal Python script that reads daily meal data from a CSV file, computes day-of-week demand trends using a moving average, and outputs a recommended meal preparation count for tomorrow with a configurable safety buffer.

Designed as a simple alternative to complex inventory software for local mess and tiffin vendors.

## Project Structure

- `data.csv`: Daily meal production and sales records
- `research.md`: Problem framing, existing solutions, and references
- `fieldwork.md`: Field visit notes and vendor interview observations
- `src/main.py`: The core calculator script
- `README.md`: Documentation and instructions

## Requirements

- Python 3.10+
- No external packages required (uses only standard library: `csv`, `datetime`, `argparse`, `collections`)

## How to Run

### Basic run (auto-detects tomorrow's weekday)
```bash
python src/main.py