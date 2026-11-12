
from pathlib import Path

from src.data.lectores import (
    leer_csv,
    leer_json,
    leer_excel
)


def cargar_datos(ruta, hoja=0):
    """
    Carga registros desde CSV, JSON o Excel.

    Devuelve una lista de diccionarios.
    No realiza validación ni clasificación.
    """

    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}"
        )

    if not ruta.is_file():
        raise ValueError(
            f"La ruta no corresponde a un archivo: {ruta}"
        )

    extension = ruta.suffix.lower()

    if extension == ".csv":
        return leer_csv(ruta)

    elif extension == ".json":
        return leer_json(ruta)

    elif extension in (".xlsx", ".xlsm"):
        return leer_excel(ruta, hoja)

    else:
        raise ValueError(
            f"Formato de archivo no compatible: {extension}"
        )


def cargar_desde_memoria(fuente):
    """Carga registros desde un adaptador de memoria."""

    registros = fuente.leer()

    if not isinstance(registros, list):
        raise TypeError(
            "La fuente de memoria debe devolver una lista."
        )

    return registros
