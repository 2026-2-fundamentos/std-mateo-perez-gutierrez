import os

import numpy as np
import pandas as pd


def _load(path: str, channel: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates()  # filas idénticas; record_id vacío sigue siendo válido
    df["channel"] = channel
    return df


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.concat(
        [
            _load("data/historical_requests_letter.csv.gz", "letter"),
            _load("data/historical_requests_web.csv.gz", "web"),
        ],
        ignore_index=True,
    )

    df["in_date"] = pd.to_datetime(df["in_date"]).dt.normalize()
    df["out_date"] = pd.to_datetime(df["out_date"]).dt.normalize()

    df["answered"] = df["out_date"].notna()
    df["pending"] = ~df["answered"]

    # Días calendario
    df["calendar_days"] = (df["out_date"] - df["in_date"]).dt.days

    # Días hábiles: lunes a viernes en (in_date, out_date]
    bd = pd.Series(np.nan, index=df.index)
    ans = df["answered"]
    start = (df.loc[ans, "in_date"] + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    end = (df.loc[ans, "out_date"] + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    bd.loc[ans] = np.busday_count(start, end)
    df["business_days"] = bd

    df["on_time"] = df["answered"] & (df["business_days"] <= 15)
    df["year"] = df["in_date"].dt.year

    # 1. Resumen por canal
    channel = (
        df.groupby("channel")
        .agg(
            requests=("channel", "size"),
            answered=("answered", "sum"),
            pending=("pending", "sum"),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
        .sort_values("channel")
        .reset_index(drop=True)
    )

    # 2. Resumen por año y canal
    yearly = (
        df.groupby(["year", "channel"])
        .agg(
            requests=("channel", "size"),
            pending=("pending", "sum"),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )

    # 3. Resumen por día de entrada (lunes a domingo, ambos canales)
    df["dow"] = df["in_date"].dt.dayofweek
    entry = (
        df.groupby("day_name")
        .agg(
            dow=("dow", "min"),
            requests=("channel", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .reset_index()
        .sort_values("dow")
        .drop(columns="dow")
        .reset_index(drop=True)
    )

    os.makedirs("submission", exist_ok=True)
    channel.to_csv("submission/channel_summary.csv", index=False)
    yearly.to_csv("submission/yearly_summary.csv", index=False)
    entry.to_csv("submission/entry_day_summary.csv", index=False)

    return channel, yearly, entry