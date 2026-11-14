"""Rol C: selección y unificación de fuentes.

Contrato que usa el servicio docente (src/services/datalab_service.py):
    cargar_datos()                         -> demostración en memoria
    cargar_datos(archivo, nombre_archivo)  -> lector según la extensión

# REVISIÓN (C-2): el estudiante escribió en src/data/trabajoo/carga_datos.py la
# firma `cargar_datos(ruta, hoja=0)`. El servicio la llama como
# `cargar_datos(archivo, archivo.name)`: el nombre se habría interpretado como
# número de hoja y `cargar_datos()` sin argumentos habría fallado. Se conserva
# la firma del contrato y se integran las verificaciones del estudiante.
"""
from pathlib import Path

from src.data.fuentes_memoria import cargar_desde_memoria
from src.data.lectores import leer_csv, leer_json, leer_excel
from src.exceptions.errores import ErrorFormatoFuente, ErrorLecturaFuente

# REVISIÓN (C-7): tabla de lectores por extensión en lugar de una cadena de if.
# Agregar un formato nuevo es agregar una línea.
# Se quitó ".xls": el proyecto instala openpyxl, que NO lee el formato antiguo
# .xls; aceptarlo prometía algo que después fallaba. ".xlsm" (Excel con macros)
# sí lo lee openpyxl, como había previsto el estudiante.
LECTORES_POR_EXTENSION = {
    "csv": leer_csv,
    "json": leer_json,
    "xlsx": leer_excel,
    "xlsm": leer_excel,
}


def _obtener_nombre(archivo, nombre_archivo):
    """Nombre del archivo: el recibido, el atributo .name o la ruta.

    # REVISIÓN (C-7): antes `nombre_archivo` era obligatorio en la práctica; si
    # llegaba "" la extensión quedaba vacía. Ahora se deduce cuando es posible.
    """
    if nombre_archivo:
        return str(nombre_archivo)
    if isinstance(archivo, (str, Path)):
        return Path(archivo).name
    return str(getattr(archivo, "name", ""))


def cargar_datos(archivo=None, nombre_archivo=""):
    """Carga la demostración en memoria o delega al lector según la extensión.

    No normaliza, no valida y no clasifica: solo entrega registros.
    """
    if archivo is None:
        return cargar_desde_memoria()

    # Trabajo del estudiante: verificación de que la ruta existe y es archivo.
    # REVISIÓN (C-5): se usan las excepciones del contrato
    # (antes FileNotFoundError y ValueError).
    if isinstance(archivo, (str, Path)):
        ruta = Path(archivo)
        if not ruta.exists():
            raise ErrorLecturaFuente(f"No se encontró el archivo: {ruta}")
        if not ruta.is_file():
            raise ErrorLecturaFuente(f"La ruta no corresponde a un archivo: {ruta}")

    nombre = _obtener_nombre(archivo, nombre_archivo)
    # Path(...).suffix devuelve ".csv"; se quita el punto y se pasa a minúsculas.
    extension = Path(nombre).suffix.lower().lstrip(".")

    lector = LECTORES_POR_EXTENSION.get(extension)
    if lector is None:
        raise ErrorFormatoFuente(
            f"Extensión no soportada: '{extension or 'sin extensión'}'. "
            f"Se aceptan: {', '.join(sorted(LECTORES_POR_EXTENSION))}"
        )
    return lector(archivo)
