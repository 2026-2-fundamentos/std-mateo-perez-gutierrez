import os

import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv("data/flights_by_carrier_day_hour.csv.gz")
    df = df.dropna(
        subset=[
            "scheduled_departure_hour",
            "reporting_airline",
            "operated_flights",
            "delayed_departure_15_flights",
        ]
    )
    df["scheduled_departure_hour"] = df["scheduled_departure_hour"].astype(int)

    # 1. Tasa nacional por hora
    hourly = (
        df.groupby("scheduled_departure_hour")[
            ["operated_flights", "delayed_departure_15_flights"]
        ]
        .sum()
        .reset_index()
    )
    hourly["delay_rate"] = (
        hourly["delayed_departure_15_flights"] / hourly["operated_flights"]
    )
    hourly = hourly.sort_values("scheduled_departure_hour").reset_index(drop=True)

    # 2. Demoras esperadas por aerolínea
    carrier_hour = (
        df.groupby(["reporting_airline", "scheduled_departure_hour"])[
            ["operated_flights", "delayed_departure_15_flights"]
        ]
        .sum()
        .reset_index()
        .merge(
            hourly[["scheduled_departure_hour", "delay_rate"]],
            on="scheduled_departure_hour",
        )
    )
    carrier_hour["expected"] = (
        carrier_hour["operated_flights"] * carrier_hour["delay_rate"]
    )

    carriers = (
        carrier_hour.groupby("reporting_airline")
        .agg(
            operated_flights=("operated_flights", "sum"),
            delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
            expected_delayed_flights=("expected", "sum"),
        )
        .reset_index()
    )
    carriers["delay_rate"] = (
        carriers["delayed_departure_15_flights"] / carriers["operated_flights"]
    )

    # 3. Razón observado / esperado
    carriers["observed_to_expected_ratio"] = (
        carriers["delayed_departure_15_flights"]
        / carriers["expected_delayed_flights"]
    )

    carriers = carriers[carriers["operated_flights"] >= 100_000].copy()
    carriers["crude_rank"] = (
        carriers["delay_rate"].rank(ascending=False, method="min").astype(int)
    )
    carriers["adjusted_rank"] = (
        carriers["observed_to_expected_ratio"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    carriers = carriers[
        [
            "reporting_airline",
            "operated_flights",
            "delayed_departure_15_flights",
            "delay_rate",
            "expected_delayed_flights",
            "observed_to_expected_ratio",
            "crude_rank",
            "adjusted_rank",
        ]
    ]
    carriers = carriers.sort_values("adjusted_rank").reset_index(drop=True)

    os.makedirs("submission", exist_ok=True)
    hourly.to_csv("submission/hourly_delay_rates.csv", index=False)
    carriers.to_csv("submission/carrier_adjusted_delays.csv", index=False)

    return hourly, carriers