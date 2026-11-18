def pregunta_01():
    import re
    import pandas as pd

    with open("data/clusters_report.txt", "r", encoding="utf-8") as f:
        lineas = f.read().splitlines()

    # Línea que inicia un clúster: número, cantidad, porcentaje con coma y '%',
    # y luego (opcionalmente) el comienzo de las palabras clave.
    patron = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+(?:,\d+)?)\s*%\s*(.*)$")

    registros = []
    actual = None

    for linea in lineas:
        m = patron.match(linea)
        if m:
            if actual is not None:
                registros.append(actual)
            actual = {
                "cluster": int(m.group(1)),
                "cantidad_de_palabras_clave": int(m.group(2)),
                "porcentaje_de_palabras_clave": float(m.group(3).replace(",", ".")),
                "texto": m.group(4).strip(),
            }
        elif actual is not None:
            # Línea de continuación: solo cuenta si tiene contenido y no es
            # un separador (----) ni una línea vacía.
            contenido = linea.strip()
            if contenido and not set(contenido) <= {"-", " "}:
                actual["texto"] += " " + contenido

    if actual is not None:
        registros.append(actual)

    filas = []
    for r in registros:
        # Normalizar espacios y limpiar el punto final / comas sobrantes
        texto = re.sub(r"\s+", " ", r["texto"]).strip().rstrip(".").strip()
        # Separar por coma, quitar espacios y descartar vacíos
        palabras = [p.strip() for p in texto.split(",") if p.strip()]
        filas.append(
            {
                "cluster": r["cluster"],
                "cantidad_de_palabras_clave": r["cantidad_de_palabras_clave"],
                "porcentaje_de_palabras_clave": r["porcentaje_de_palabras_clave"],
                "principales_palabras_clave": ", ".join(palabras),
            }
        )

    return pd.DataFrame(
        filas,
        columns=[
            "cluster",
            "cantidad_de_palabras_clave",
            "porcentaje_de_palabras_clave",
            "principales_palabras_clave",
        ],
    )
