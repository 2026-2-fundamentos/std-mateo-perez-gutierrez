def pregunta_03():
    import pandas as pd

    df = pd.read_csv("data/tbl0.tsv", sep="\t")
    return df.groupby("c1").size()
