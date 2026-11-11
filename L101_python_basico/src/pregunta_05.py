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


def pregunta_05():
    """(letra, máximo, mínimo) de `value` por letra."""
    valores = defaultdict(list)
    for f in _leer():
        valores[f[0]].append(int(f[1]))
    return [(l, max(v), min(v)) for l, v in sorted(valores.items())]
