def pregunta_13():
    import pandas as pd

    tbl0 = pd.read_csv("data/tbl0.tsv", sep="\t")
    tbl2 = pd.read_csv("data/tbl2.tsv", sep="\t")
    merged = pd.merge(tbl0, tbl2, on="c0")
    return merged.groupby("c1")["c5b"].sum()
