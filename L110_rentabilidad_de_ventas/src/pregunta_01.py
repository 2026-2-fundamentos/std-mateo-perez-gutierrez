
import pandas as pd
import os


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    df = pd.read_csv(
        "data/superstore_orders.csv.gz",
        sep=None,
        engine="python",
        decimal=","
)

    # Crear margen de utilidad
    df["profit_margin"] = df["Profit"] / df["Sales"]

    # Identificar líneas con pérdida
    df["loss_line"] = df["Profit"] < 0

    # Calcular pérdida como número positivo
    df["lost_profit"] = df["Profit"].apply(
        lambda x: -x if x < 0 else 0
    )

    # Clasificar descuentos
    def clasificar_descuento(descuento):
        if descuento == 0:
            return "0%"
        elif descuento <= 0.05:
            return "1%-5%"
        elif descuento <= 0.10:
            return "6%-10%"
        else:
            return "más de 10%"

    df["discount_band"] = df["Discount"].apply(clasificar_descuento)

    # --------------------------------------------------
    # 1. RESUMEN DE RENTABILIDAD
    # --------------------------------------------------

    profitability_summary = pd.DataFrame([{
        "lines": len(df),
        "orders": df["Order ID"].nunique(),
        "sales": df["Sales"].sum(),
        "profit": df["Profit"].sum(),
        "profit_margin": df["Profit"].sum() / df["Sales"].sum(),
        "loss_lines": df["loss_line"].sum(),
        "loss_line_rate": df["loss_line"].mean(),
        "lost_profit": df["lost_profit"].sum()
    }])

    # --------------------------------------------------
    # 2. RESUMEN POR RANGO DE DESCUENTO
    # --------------------------------------------------

    discount_summary = df.groupby("discount_band").agg(
        lines=("Profit", "count"),
        sales=("Sales", "sum"),
        profit=("Profit", "sum"),
        loss_line_rate=("loss_line", "mean"),
        lost_profit=("lost_profit", "sum")
    ).reset_index()

    # Calcular margen por rango
    discount_summary["profit_margin"] = (
        discount_summary["profit"] / discount_summary["sales"]
    )

    # Orden establecido para los descuentos
    orden = ["0%", "1%-5%", "6%-10%", "más de 10%"]

    discount_summary["discount_band"] = pd.Categorical(
        discount_summary["discount_band"],
        categories=orden,
        ordered=True
    )

    discount_summary = discount_summary.sort_values(
        "discount_band"
    ).reset_index(drop=True)

    discount_summary["discount_band"] = (
        discount_summary["discount_band"].astype(str)
    )

    discount_summary = discount_summary[
        ["discount_band", "lines", "sales", "profit",
         "profit_margin", "loss_line_rate", "lost_profit"]
    ]

    # --------------------------------------------------
    # 3. SEGMENTOS Y CATEGORÍAS PRIORITARIAS
    # --------------------------------------------------

    priority_segments = df.groupby(
        ["Customer Segment", "Product Category"]
    ).agg(
        lines=("Profit", "count"),
        sales=("Sales", "sum"),
        profit=("Profit", "sum"),
        lost_profit=("lost_profit", "sum")
    ).reset_index()

    # Conservar grupos con al menos 100 líneas
    priority_segments = priority_segments[
        priority_segments["lines"] >= 100
    ]

    # Calcular margen
    priority_segments["profit_margin"] = (
        priority_segments["profit"] / priority_segments["sales"]
    )

    # Ordenar por pérdidas y seleccionar los cinco primeros
    priority_segments = priority_segments.sort_values(
        "lost_profit", ascending=False
    ).head(5).reset_index(drop=True)

    priority_segments = priority_segments[
        ["Customer Segment", "Product Category", "lines",
         "sales", "profit", "profit_margin", "lost_profit"]
    ]

    # --------------------------------------------------
    # EXPORTAR ARCHIVOS
    # --------------------------------------------------

    os.makedirs("submission", exist_ok=True)

    profitability_summary.to_csv(
        "submission/profitability_summary.csv", index=False
    )

    discount_summary.to_csv(
        "submission/discount_summary.csv", index=False
    )

    priority_segments.to_csv(
        "submission/priority_segments.csv", index=False
    )

    return profitability_summary, discount_summary, priority_segments
