def pregunta_01():
    import json
    import os

    import numpy as np
    import pandas as pd

    df = pd.read_csv("data/insurance.csv.gz")

    # ---------- Generalización ----------
    df["age_group"] = pd.cut(
        df["age"],
        bins=[-np.inf, 29, 39, 49, np.inf],
        labels=["18-29", "30-39", "40-49", "50-64"],
    ).astype(str)

    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[-np.inf, 18.5, 25, 30, np.inf],
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
        right=False,  # [18.5, 25), [25, 30), [30, inf)
    ).astype(str)

    df["children_group"] = pd.cut(
        df["children"],
        bins=[-np.inf, 0, 2, np.inf],
        labels=["0", "1-2", "3+"],
    ).astype(str)

    df["is_smoker"] = (df["smoker"] == "yes").astype(int)

    # ---------- Riesgo original (sin generalizar) ----------
    original_qi = ["age", "sex", "bmi", "children", "region"]
    original_sizes = df.groupby(original_qi)["charges"].transform("size")
    original_k = int(original_sizes.min())
    original_unique_records = int((original_sizes == 1).sum())

    # ---------- Esquemas ----------
    schemes_qi = {
        "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
        "without_children": ["age_group", "sex", "bmi_group", "region"],
    }
    K = 5

    schemes = {}
    masks = {}
    for name, qi in schemes_qi.items():
        g = df.groupby(qi)
        size = g["charges"].transform("size")
        smoker_mean = g["is_smoker"].transform("mean")

        published_mask = size >= K
        masks[name] = published_mask

        classes = g.size()
        published_classes = classes[classes >= K]

        pub = df[published_mask]
        pub_size = size[published_mask]
        pub_mean = smoker_mean[published_mask]
        no_div = (pub_mean == 0) | (pub_mean == 1)

        # clases publicadas sin diversidad
        class_stats = pub.groupby(qi)["is_smoker"].mean()
        classes_no_div = int(((class_stats == 0) | (class_stats == 1)).sum())

        schemes[name] = {
            "quasi_identifiers": qi,
            "equivalence_classes": int(len(classes)),
            "k_before_suppression": int(classes.min()),
            "suppressed_records": int((~published_mask).sum()),
            "published_records": int(published_mask.sum()),
            "published_classes": int(len(published_classes)),
            "classes_without_smoker_diversity": classes_no_div,
            "records_without_smoker_diversity": int(no_div.sum()),
        }

    # ---------- Selección ----------
    selected = min(schemes, key=lambda s: schemes[s]["suppressed_records"])
    published = df[masks[selected]]

    report = {
        "original_k": original_k,
        "original_unique_records": original_unique_records,
        "schemes": schemes,
        "selected_scheme": selected,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(published["charges"].mean()),
        "smoker_rate_original": float(df["is_smoker"].mean()),
        "smoker_rate_published": float(published["is_smoker"].mean()),
    }

    # ---------- Salidas ----------
    os.makedirs("submission", exist_ok=True)

    with open("submission/privacy_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    out_cols = schemes_qi[selected] + ["smoker", "charges"]
    published[out_cols].to_csv("submission/insurance_published.csv", index=False)

    return report
