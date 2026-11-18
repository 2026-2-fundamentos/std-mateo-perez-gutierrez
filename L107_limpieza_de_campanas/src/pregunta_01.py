import glob
import os

import pandas as pd


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # ---------- Lectura directa de los .csv.gz ----------
    archivos = sorted(glob.glob("data/bank-marketing-campaing-*.csv.gz"))
    df = pd.concat(
        (pd.read_csv(f, compression="gzip") for f in archivos),
        ignore_index=True,
    )

    # Si cada archivo trae un índice espurio, se descarta
    df = df.loc[:, ~df.columns.astype(str).str.contains(r"^Unnamed")]

    # ---------- 1. client ----------
    client = df[
        ["client_id", "age", "job", "marital", "education", "credit_default", "mortgage"]
    ].copy()

    client["job"] = (
        client["job"].astype(str).str.replace(".", "", regex=False).str.replace("-", "_", regex=False)
    )

    client["education"] = client["education"].astype(str).str.replace(".", "_", regex=False)
    client["education"] = client["education"].replace("unknown", pd.NA)

    client["credit_default"] = (client["credit_default"] == "yes").astype(int)
    client["mortgage"] = (client["mortgage"] == "yes").astype(int)

    # ---------- 2. campaign ----------
    campaign = df[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
            "month",
            "day",
        ]
    ].copy()

    campaign["previous_outcome"] = (campaign["previous_outcome"] == "success").astype(int)
    campaign["campaign_outcome"] = (campaign["campaign_outcome"] == "yes").astype(int)

    meses = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    mes = campaign["month"].astype(str).str.strip().str.lower().str[:3].map(meses)

    campaign["last_contact_date"] = pd.to_datetime(
        {"year": 2022, "month": mes, "day": campaign["day"]}
    ).dt.strftime("%Y-%m-%d")

    campaign = campaign.drop(columns=["month", "day"])

    # ---------- 3. economics ----------
    economics = df[["client_id", "cons_price_idx", "euribor_three_months"]].copy()

    # ---------- Guardado ----------
    os.makedirs("submission", exist_ok=True)
    client.to_csv("submission/client.csv", index=False)
    campaign.to_csv("submission/campaign.csv", index=False)
    economics.to_csv("submission/economics.csv", index=False)

    return client, campaign, economics
