def pregunta_09():
    import pandas as pd

    df = pd.read_csv("data/tbl0.tsv", sep="\t")
    df["year"] = df["c3"].astype(str).str[:4]
    return df
