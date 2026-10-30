import requests
import pandas as pd

BASE_URL = "https://api.worldbank.org/v2/country/NPL/indicator/"

INDICATORS = {
    "GDP Growth": "NY.GDP.MKTP.KD.ZG",
    "Inflation Rate": "FP.CPI.TOTL.ZG",
    "Remittances": "BX.TRF.PWKR.DT.GD.ZS",
    "Exports": "NE.EXP.GNFS.ZS",
    "Imports": "NE.IMP.GNFS.ZS"
}


def fetch_indicator(indicator_code):
    """Fetch historical economic data for Nepal from the World Bank."""

    url = BASE_URL + indicator_code

    params = {
        "format": "json",
        "per_page": 100
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Unexpected World Bank API response")

    records = data[1]

    if not isinstance(records, list):
        raise ValueError("No indicator records returned")

    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=["year", "value"])

    df = df[["date", "value"]].copy()

    df = df.rename(columns={"date": "year"})

    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    df = df.dropna(subset=["year", "value"])

    df["year"] = df["year"].astype(int)

    df = df.sort_values("year")

    df = df.reset_index(drop=True)

    return df


def get_latest_stats(df):
    """Get the latest observation and change from the previous one."""

    if df.empty:
        return None

    latest = df.iloc[-1]

    latest_value = float(latest["value"])
    latest_year = int(latest["year"])

    previous_value = None
    previous_year = None
    delta = None

    if len(df) >= 2:

        previous = df.iloc[-2]

        previous_value = float(previous["value"])
        previous_year = int(previous["year"])

        delta = latest_value - previous_value

    return {
        "latest_value": latest_value,
        "latest_year": latest_year,
        "previous_value": previous_value,
        "previous_year": previous_year,
        "delta": delta
    }