def pregunta_12():
    import pandas as pd

    df = pd.read_csv("data/tbl2.tsv", sep="\t")
    df["c5"] = df["c5a"] + ":" + df["c5b"].astype(str)
    return (
        df.groupby("c0")["c5"]
        .apply(lambda s: ",".join(sorted(s)))
        .reset_index()
    )
