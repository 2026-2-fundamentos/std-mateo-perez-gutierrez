def pregunta_10():
    import pandas as pd

    df = pd.read_csv("data/tbl0.tsv", sep="\t")
    df = df.sort_values(["c1", "c2"])
    return (
        df.groupby("c1")["c2"]
        .apply(lambda s: ":".join(str(v) for v in s))
        .to_frame()
    )
