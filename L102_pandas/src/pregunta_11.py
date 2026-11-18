def pregunta_11():
    import pandas as pd

    df = pd.read_csv("data/tbl1.tsv", sep="\t")
    return (
        df.groupby("c0")["c4"]
        .apply(lambda s: ",".join(sorted(s)))
        .reset_index()
    )
