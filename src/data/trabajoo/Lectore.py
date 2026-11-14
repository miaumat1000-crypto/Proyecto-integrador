
import csv
import json
from pathlib import Path


def leer_csv(ruta):
    """Lee un archivo CSV y devuelve una lista de diccionarios."""

    ruta = Path(ruta)

    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        return [dict(fila) for fila in lector]


def leer_json(ruta):
    """Lee un archivo JSON y devuelve sus registros."""

    ruta = Path(ruta)

    with ruta.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if isinstance(datos, list):
        return datos

    if isinstance(datos, dict):
        registros = datos.get("registros")

        if isinstance(registros, list):
            return registros

    raise ValueError(
        "El JSON debe contener una lista de registros "
        "o una clave 'registros' con una lista."
    )


def leer_excel(ruta, hoja=0):
    """Lee una hoja de Excel y devuelve una lista de diccionarios."""

    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise ImportError(
            "Se necesita instalar openpyxl para leer Excel."
        ) from error

    ruta = Path(ruta)

    libro = load_workbook(
        filename=ruta,
        read_only=True,
        data_only=True
    )

    try:
        if isinstance(hoja, int):
            if hoja < 0 or hoja >= len(libro.sheetnames):
                raise ValueError("El índice de hoja no existe.")
            pagina = libro.worksheets[hoja]
        else:
            if hoja not in libro.sheetnames:
                raise ValueError(f"No existe la hoja: {hoja}")
            pagina = libro[hoja]

        filas = pagina.iter_rows(values_only=True)

        encabezados = next(filas, None)

        if encabezados is None:
            return []

        encabezados = list(encabezados)

        if any(
            encabezado is None or str(encabezado).strip() == ""
            for encabezado in encabezados
        ):
            raise ValueError("El Excel contiene encabezados vacíos.")

        if len(set(encabezados)) != len(encabezados):
            raise ValueError("El Excel contiene encabezados duplicados.")

        registros = []

        for fila in filas:
            registro = dict(zip(encabezados, fila))

            if all(valor is None for valor in registro.values()):
                continue

            registros.append(registro)

        return registros

    finally:
        libro.close()
