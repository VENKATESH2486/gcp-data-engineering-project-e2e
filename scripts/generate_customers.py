"""
Generate realistic customer data for the Data Engineering Pipeline.

Usage:
    python scripts/generate_customers.py
    python scripts/generate_customers.py --rows 10000
"""

from pathlib import Path
from datetime import datetime

import argparse
import random

import pandas as pd
from faker import Faker

fake = Faker()

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

CUSTOMER_FILE = OUTPUT_DIR / "customer.csv"

CITIES = [
    ("Hyderabad", "India"),
    ("Bengaluru", "India"),
    ("Chennai", "India"),
    ("Mumbai", "India"),
    ("Delhi", "India"),
    ("New York", "USA"),
    ("Seattle", "USA"),
    ("Chicago", "USA"),
    ("London", "United Kingdom"),
    ("Berlin", "Germany"),
    ("Sydney", "Australia"),
]

EMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "icloud.com",
]

def generate_customer(customer_id: int) -> dict:

    first_name = fake.first_name()
    last_name = fake.last_name()

    city, country = random.choice(CITIES)

    email = (
        f"{first_name}.{last_name}"
        f"{random.randint(1,999)}"
        f"@{random.choice(EMAIL_DOMAINS)}"
    ).lower()

    created_at = fake.date_between(
        start_date="-3y",
        end_date="today",
    )

    return {
        "customer_id": customer_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "city": city,
        "country": country,
        "created_at": created_at.strftime("%Y-%m-%d"),
    }

def generate_customers(rows: int) -> pd.DataFrame:

    customers = [
        generate_customer(i)
        for i in range(1, rows + 1)
    ]

    return pd.DataFrame(customers)

def save_dataframe(df: pd.DataFrame, output_file: Path) -> None:

    df.to_csv(output_file, index=False)

    print(f"Generated {len(df):,} customers")
    print(f"Saved to {output_file}")

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--rows",
        type=int,
        default=200,
        help="Number of customers to generate",
    )

    args = parser.parse_args()

    df = generate_customers(args.rows)

    save_dataframe(df, CUSTOMER_FILE)


if __name__ == "__main__":
    main()

    