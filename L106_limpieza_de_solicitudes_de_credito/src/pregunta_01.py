def pregunta_01():
    import os
    import re
    import unicodedata

    import pandas as pd

    COLUMNAS = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "comuna_ciudadano",
        "fecha_de_beneficio",
        "monto_del_credito",
        "línea_credito",
    ]

    df = pd.read_csv(
        "data/solicitudes_de_credito.csv.gz",
        sep=";",
        compression="gzip",
        dtype=str,
        encoding="utf-8",
    )

    # Eliminar la columna de índice espuria (Unnamed: 0, etc.)
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed", case=False)]
    df.columns = [c.strip() for c in df.columns]
    df = df[COLUMNAS].copy()

    # ---------- Campos de texto ----------
    texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]

    def limpiar_texto(x):
        if pd.isna(x):
            return x
        x = str(x).lower()
        x = re.sub(r"[_\-]+", " ", x)       # guiones y guiones bajos -> espacio
        x = re.sub(r"\s+", " ", x).strip()  # espacios múltiples
        return x if x else pd.NA

    for c in texto:
        df[c] = df[c].map(limpiar_texto)

    # comuna_ciudadano: se limpia, pero los faltantes se conservan
    df["comuna_ciudadano"] = df["comuna_ciudadano"].map(
        lambda x: x if pd.isna(x) else (re.sub(r"\s+", " ", str(x).lower()).strip() or pd.NA)
    )

    # ---------- Estrato ----------
    df["estrato"] = pd.to_numeric(
        df["estrato"].astype("string").str.extract(r"(\d+)", expand=False),
        errors="coerce",
    )

    # ---------- Monto ----------
    def limpiar_monto(x):
        if pd.isna(x):
            return pd.NA
        x = re.sub(r"[^\d,.\-]", "", str(x))   # quita $, espacios, etc.
        x = re.sub(r"[.,]\d{1,2}$", "", x)     # decimales finales (.00 / ,00)
        x = re.sub(r"[.,]", "", x)             # separadores de miles
        return x if x else pd.NA

    df["monto_del_credito"] = pd.to_numeric(
        df["monto_del_credito"].map(limpiar_monto), errors="coerce"
    )

    # ---------- Fechas ----------
    def parsear_fecha(x):
        if pd.isna(x):
            return pd.NaT
        x = str(x).strip()
        if re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}", x):   # AAAA-MM-DD
            return pd.to_datetime(x, errors="coerce", format="mixed")
        return pd.to_datetime(x, errors="coerce", dayfirst=True, format="mixed")  # DD/MM/AAAA

    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].map(parsear_fecha)

    # ---------- Registros incompletos (excepto comuna_ciudadano) ----------
    obligatorias = [c for c in COLUMNAS if c != "comuna_ciudadano"]
    df = df.dropna(subset=obligatorias)

    # Tipos finales
    df["estrato"] = df["estrato"].astype(int)
    df["monto_del_credito"] = df["monto_del_credito"].astype("int64")
    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].dt.strftime("%Y-%m-%d")

    # ---------- Duplicados (después de normalizar) ----------
    df = df.drop_duplicates().reset_index(drop=True)

    # ---------- Guardar ----------
    os.makedirs("submission", exist_ok=True)
    df[COLUMNAS].to_csv(
        "submission/solicitudes_de_credito.csv",
        sep=";",
        index=False,
        encoding="utf-8",
    )