import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import duckdb
from datetime import datetime, timezone

load_dotenv()
api_key = os.getenv("TRAVELPAYOUTS_TOKEN")
ORIGIN = "GDN"
DESTINATIONS = ["FNC", "TBS", "KUT", "IST"]
DEPARTURE_AT = "2026-12"
CURRENCY = "pln"  # API default is in rubles
ONE_WAY = "false"  # round trips; lowercase text, because default False would be sent as "False"
DB_PATH = Path("data/flights.duckdb")


def fetch_flights(origin, destination, departure_at):
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    headers = {"X-Access-Token": api_key}
    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_at,
        "currency": CURRENCY,
        "one_way": ONE_WAY,
    }
    response = requests.get(url, params=params, headers=headers)

    response.raise_for_status()

    payload = response.json()

    # the API can return HTTP 200 and still have success: false
    if not payload["success"]:
        raise RuntimeError(f"API error: {payload['error']}")
    return payload


def main():
    checked_at = datetime.now(timezone.utc)
    frames = []

    for destination in DESTINATIONS:
        result = fetch_flights(ORIGIN, destination, DEPARTURE_AT)
        offers = result["data"]

        if len(offers) == 0:
            print(f"No offers: {ORIGIN} {destination}")
            continue

        frames.append(pd.json_normalize(offers))

    if len(frames) == 0:
        print("No offers on any route")
        return

    df = pd.concat(frames, ignore_index=True)

    df["checked_at"] = checked_at

    Path("data").mkdir(exist_ok=True)

    with duckdb.connect(str(DB_PATH)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        # empty table - only df columns; rows are only added by the INSERT below
        con.execute(
            "CREATE TABLE IF NOT EXISTS raw.flight_prices AS SELECT * FROM df LIMIT 0"
        )
        # match columns by name, API doesn't guarantee column order
        con.execute("INSERT INTO raw.flight_prices BY NAME SELECT * FROM df")
        rows = con.execute("SELECT COUNT(*) FROM raw.flight_prices").fetchone()[0]
        checks = con.execute(
            "SELECT COUNT(DISTINCT checked_at) FROM raw.flight_prices"
        ).fetchone()[0]
    print(f"rows = {rows}, checks = {checks}")


if __name__ == "__main__":
    main()
