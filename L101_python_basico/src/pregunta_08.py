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


def pregunta_08():
    """(valor, letras únicas ordenadas alfabéticamente)."""
    grupos = defaultdict(set)
    for f in _leer():
        grupos[int(f[1])].add(f[0])
    return [(v, sorted(letras)) for v, letras in sorted(grupos.items())]
