def main():
    """
    Genera el reporte de calidad de `data/ventas.csv.gz` sin limpiar los datos,
    lo guarda en `submission/data_quality_report.json` y lo retorna.
    """

    import json
    import os
    import re

    import pandas as pd

    required_columns = [
        "supplier_id",
        "supplier",
        "country",
        "city",
        "purchase_date",
        "amount",
        "discount",
        "weight",
        "units",
        "unit_price",
        "contact_email",
    ]

    # ------------------------------------------------------------------
    # Lectura sin modificar valores: todo como texto, sin convertir a NaN
    # ------------------------------------------------------------------
    path = os.path.join("data", "ventas.csv.gz")
    read_kwargs = dict(dtype=str, keep_default_na=False, na_filter=False)
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", **read_kwargs)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1", **read_kwargs)

    # ------------------------------------------------------------------
    # Normalización de encabezados
    # ------------------------------------------------------------------
    df.columns = [
        str(c).replace("\ufeff", "").strip().lower().replace(" ", "_")
        for c in df.columns
    ]
    columns = list(df.columns)

    # ------------------------------------------------------------------
    # Columnas requeridas / inesperadas
    # ------------------------------------------------------------------
    missing_required_columns = sorted(set(required_columns) - set(columns))
    unexpected_columns = sorted(set(columns) - set(required_columns))

    # ------------------------------------------------------------------
    # Duplicados
    # ------------------------------------------------------------------
    duplicate_row_count = int(df.duplicated().sum())

    if "supplier_id" in df.columns:
        duplicate_supplier_id_row_count = int(
            df["supplier_id"].duplicated(keep=False).sum()
        )
    else:
        duplicate_supplier_id_row_count = 0

    # ------------------------------------------------------------------
    # Valores faltantes: celdas vacías y "N/A"
    # ------------------------------------------------------------------
    def is_missing(series):
        stripped = series.str.strip()
        return (stripped == "") | (stripped == "N/A")

    missing_value_count_by_column = {
        col: int(is_missing(df[col]).sum()) for col in columns
    }

    # ------------------------------------------------------------------
    # Correos inválidos (usuario@dominio.extension); no se cuentan faltantes
    # ------------------------------------------------------------------
    invalid_email_count = 0
    if "contact_email" in df.columns:
        emails = df.loc[~is_missing(df["contact_email"]), "contact_email"]
        pattern = re.compile(r"[^@\s]+@[^@\s.]+(\.[^@\s.]+)+")
        invalid_email_count = int(
            sum(1 for e in emails if pattern.fullmatch(e) is None)
        )

    # ------------------------------------------------------------------
    # Unidades inválidas: numéricas que no son enteros positivos
    # ------------------------------------------------------------------
    invalid_unit_count = 0
    if "units" in df.columns:
        units = df.loc[~is_missing(df["units"]), "units"]
        numeric = pd.to_numeric(units, errors="coerce").dropna()
        invalid_unit_count = int(
            sum(1 for v in numeric if v <= 0 or not float(v).is_integer())
        )

    # ------------------------------------------------------------------
    # Valores distintos de country, tal como aparecen
    # ------------------------------------------------------------------
    if "country" in df.columns:
        country = df["country"]
        country_values = sorted(country[~is_missing(country)].unique().tolist())
    else:
        country_values = []

    # ------------------------------------------------------------------
    # Reporte
    # ------------------------------------------------------------------
    report = {
        "row_count": int(len(df)),
        "column_count": int(len(columns)),
        "missing_required_columns": missing_required_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    os.makedirs("submission", exist_ok=True)
    with open(
        os.path.join("submission", "data_quality_report.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return report