"""Rol B: excepciones y registro de incidencias.

Jerarquía de excepciones de DataLab:

    DataLabError                      (base, CATEGORIA = "PROCESAMIENTO")
    ├── ErrorValidacion               "VALIDACION"
    ├── ErrorConversion               "CONVERSION"
    ├── ErrorFormatoFuente            "FORMATO_FUENTE"
    │   └── ErrorEstructuraRegistro   "ESTRUCTURA_REGISTRO"
    ├── ErrorLecturaFuente            "LECTURA_FUENTE"
    └── ErrorEventoSensor             "EVENTO_SENSOR"
        ├── ErrorTimeoutSensor        "TIMEOUT_SENSOR"
        ├── ErrorPaqueteIncompleto    "PAQUETE_INCOMPLETO"
        └── ErrorLecturaIntermitente  "LECTURA_INTERMITENTE"
"""
from datetime import datetime, timezone


# REVISIÓN (B-5): cada excepción tiene un atributo de clase CATEGORIA.
# Así la excepción "sabe" su categoría y el procesamiento no necesita una
# cadena de if/elif con isinstance para decidirla. Las subclases heredan el
# atributo o lo redefinen.
class DataLabError(Exception):
    """Excepción base de la aplicación."""
    CATEGORIA = "PROCESAMIENTO"


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""
    CATEGORIA = "VALIDACION"


# REVISIÓN (B-8): excepción propia para la conversión de texto a número.
# Antes la conversión fallida se reportaba como ErrorValidacion.
class ErrorConversion(DataLabError):
    """No fue posible convertir un valor al tipo esperado."""
    CATEGORIA = "CONVERSION"


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""
    CATEGORIA = "FORMATO_FUENTE"


# REVISIÓN (B-3): excepción para UN registro roto (fila irregular de un CSV,
# un elemento que no es diccionario, etc.). Es un caso particular de formato,
# por eso hereda de ErrorFormatoFuente.
class ErrorEstructuraRegistro(ErrorFormatoFuente):
    """Un registro individual no tiene la estructura esperada."""
    CATEGORIA = "ESTRUCTURA_REGISTRO"


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""
    CATEGORIA = "LECTURA_FUENTE"


# REVISIÓN (B-3): eventos técnicos simulados por los sensores. Los datasets
# traen la columna `observacion_tecnica` con valores SIMULACION_*. No son datos
# de mala calidad (Rol A): son fallas del origen y se reportan como errores.
class ErrorEventoSensor(DataLabError):
    """El sensor reportó un evento técnico durante la lectura."""
    CATEGORIA = "EVENTO_SENSOR"


class ErrorTimeoutSensor(ErrorEventoSensor):
    """El sensor no respondió a tiempo."""
    CATEGORIA = "TIMEOUT_SENSOR"


class ErrorPaqueteIncompleto(ErrorEventoSensor):
    """El paquete de datos del sensor llegó incompleto."""
    CATEGORIA = "PAQUETE_INCOMPLETO"


class ErrorLecturaIntermitente(ErrorEventoSensor):
    """La lectura del sensor fue intermitente."""
    CATEGORIA = "LECTURA_INTERMITENTE"


# REVISIÓN (B-3): tabla que relaciona el texto del evento con su excepción.
# Agregar un evento nuevo es agregar una línea; el ciclo de procesamiento no
# cambia. Un evento SIMULACION_* que no esté aquí usa la clase general.
EVENTOS_TECNICOS = {
    "SIMULACION_TIMEOUT_SENSOR": ErrorTimeoutSensor,
    "SIMULACION_PAQUETE_INCOMPLETO": ErrorPaqueteIncompleto,
    "SIMULACION_LECTURA_INTERMITENTE": ErrorLecturaIntermitente,
}


def crear_reporte_error(origen, identificador, mensaje, categoria=None):
    """Construye un diccionario de error normalizado con fecha/hora y categoría.

    `mensaje` puede ser un texto o una excepción. Si es una excepción de DataLab
    y no se indica la categoría, se toma de su atributo CATEGORIA.
    """
    # REVISIÓN (B-5): la categoría puede deducirse de la excepción.
    if categoria is None:
        categoria = getattr(mensaje, "CATEGORIA", DataLabError.CATEGORIA)

    return {
        # REVISIÓN (B-7): la clave era "timestamp". El README pide
        # "identificador, categoría, origen, mensaje y fecha/hora UTC", así que
        # se usa "fecha_hora". timezone.utc deja explícita la zona horaria y
        # timespec="seconds" quita los microsegundos para que sea legible en la
        # tabla y en el CSV que se descarga desde Streamlit.
        "identificador": identificador,
        "categoria": categoria,
        "origen": origen,
        "mensaje": str(mensaje),
        "fecha_hora": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
