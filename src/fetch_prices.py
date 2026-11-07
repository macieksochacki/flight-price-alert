import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import duckdb

load_dotenv()
api_key = os.getenv("TRAVELPAYOUTS_TOKEN")
ORIGIN = "GDN"
DESTINATION = "FNC"
DEPARTURE_AT = "2026-12"
CURRENCY = "pln"  # API default is in rubles
ONE_WAY = "false"  # round trips; lowercase text, because default False would be sent as "False"


def fetch_flights(origin, destination, departure_at):
    url = f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    headers = {"X-Access-Token": api_key}
    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_at,
        "currency": CURRENCY,
        "one_way": ONE_WAY,
    }
    response = requests.get(url, params=params, headers=headers)
    print(response.url)

    response.raise_for_status()

    payload = response.json()

    # the API can return HTTP 200 and still have success: false
    if not payload["success"]:
        raise RuntimeError(f"API error: {payload['error']}")
    return payload


result = fetch_flights(ORIGIN, DESTINATION, DEPARTURE_AT)
offers = result["data"]
print(len(offers))
print(offers[0]["price"])
