def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.
    """

    import os

    import pandas as pd

    base_dir = "data"
    output_dir = "submission"
    os.makedirs(output_dir, exist_ok=True)

    for split in ["train", "test"]:
        split_dir = os.path.join(base_dir, split)
        rows = []

        for target in sorted(os.listdir(split_dir)):
            target_dir = os.path.join(split_dir, target)
            if not os.path.isdir(target_dir):
                continue

            for filename in sorted(os.listdir(target_dir)):
                if not filename.endswith(".txt"):
                    continue

                file_path = os.path.join(target_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    phrase = f.read().strip()

                rows.append({"phrase": phrase, "target": target})

        df = pd.DataFrame(rows, columns=["phrase", "target"])
        df.to_csv(
            os.path.join(output_dir, f"{split}_dataset.csv"),
            index=False,
            encoding="utf-8",
        )
