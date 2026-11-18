def pregunta_05():
    import pandas as pd

    df = pd.read_csv("data/tbl0.tsv", sep="\t")
    return df.groupby("c1")["c2"].max()
