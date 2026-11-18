def pregunta_01():
    import pandas as pd

    df = pd.read_csv("data/tbl0.tsv", sep="\t")
    return len(df)
