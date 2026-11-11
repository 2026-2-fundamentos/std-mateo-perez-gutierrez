import csv
import gzip
from collections import defaultdict


def _leer():
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8", newline="") as f:
        lineas = f.read().splitlines()
    sep = "\t" if lineas and "\t" in lineas[0] else ","
    return [
        [c.strip() for c in fila]
        for fila in csv.reader(lineas, delimiter=sep)
        if len(fila) >= 5 and fila[1].strip().lstrip("-").isdigit()
    ]


def pregunta_12():
    """Suma de todos los valores de `metrics` por letra."""
    sumas = defaultdict(int)
    for f in _leer():
        for par in f[4].split(","):
            sumas[f[0]] += int(par.split(":")[1])
    return dict(sorted(sumas.items()))
