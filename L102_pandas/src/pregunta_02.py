def pregunta_02():
    import pandas as pd

    df = pd.read_csv("data/tbl0.tsv", sep="\t")
    return df.shape[1]
