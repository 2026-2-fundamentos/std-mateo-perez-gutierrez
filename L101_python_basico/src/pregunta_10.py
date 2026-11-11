import csv
import gzip


def _leer():
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8", newline="") as f:
        lineas = f.read().splitlines()
    sep = "\t" if lineas and "\t" in lineas[0] else ","
    return [
        [c.strip() for c in fila]
        for fila in csv.reader(lineas, delimiter=sep)
        if len(fila) >= 5 and fila[1].strip().lstrip("-").isdigit()
    ]


def pregunta_10():
    """(letra, cantidad de codes, cantidad de pares de metrics) por registro."""
    return [
        (f[0], len(f[3].split(",")), len(f[4].split(",")))
        for f in _leer()
    ]
