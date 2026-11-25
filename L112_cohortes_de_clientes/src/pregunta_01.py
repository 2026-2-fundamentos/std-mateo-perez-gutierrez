import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    df = pd.read_csv("data/sales.csv.gz", usecols=["CustomerID", "OrderDate"])
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df = df.dropna(subset=["CustomerID", "OrderDate"])

    df["order_month"] = df["OrderDate"].dt.to_period("M")
    df["cohort"] = df.groupby("CustomerID")["order_month"].transform("min")
    df["period_index"] = (
        (df["order_month"].dt.year - df["cohort"].dt.year) * 12
        + (df["order_month"].dt.month - df["cohort"].dt.month)
    )

    cohort = (
        df.groupby(["cohort", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )
    sizes = (
        cohort[cohort["period_index"] == 0]
        .set_index("cohort")["active_customers"]
        .rename("cohort_size")
    )
    cohort = cohort.merge(sizes, on="cohort")
    cohort["retention_rate"] = cohort["active_customers"] / cohort["cohort_size"]
    cohort["cohort_month"] = cohort["cohort"].astype(str)
    cohort = (
        cohort.sort_values(["cohort", "period_index"])[
            [
                "cohort_month",
                "period_index",
                "active_customers",
                "cohort_size",
                "retention_rate",
            ]
        ]
        .reset_index(drop=True)
    )

    os.makedirs("submission", exist_ok=True)
    cohort.to_csv("submission/cohort_retention.csv", index=False)

    # Mapa de calor: lo no observable queda como NaN (vacío)
    pivot = cohort.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    ).sort_index()
    data = np.ma.masked_invalid(pivot.to_numpy())

    fig, ax = plt.subplots(
        figsize=(max(8, 0.6 * pivot.shape[1] + 3), max(5, 0.4 * pivot.shape[0] + 2))
    )
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad("white")
    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("Período (meses desde la primera compra)")
    ax.set_ylabel("Cohorte (mes de primera compra)")
    ax.set_title("Retención de clientes por cohorte")

    values = pivot.to_numpy()
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            v = values[i, j]
            if not np.isnan(v):
                ax.text(
                    j,
                    i,
                    f"{v:.0%}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white" if v > 0.5 else "black",
                )

    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    fig.tight_layout()
    fig.savefig("submission/cohort_retention_heatmap.png", dpi=150)
    plt.close(fig)

    return cohort