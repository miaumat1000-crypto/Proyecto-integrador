"""Rol B: orquestación del procesamiento.

Flujo de cada registro:

    1. Revisión técnica    -> ¿el registro está roto o trae un evento del sensor?
                              Sí: va a `errores` (Rol B).
    2. Normalización       -> copia estandarizada (Rol A).
    3. Validación          -> ¿el dato es de buena calidad?
                              No: va a `registros_invalidos` con sus motivos (Rol A).
    4. Conversión          -> valor de texto a float.
    5. Clasificación       -> clasificar_valor(valor, tipo), regla centralizada.
    6. Resumen             -> indicadores calculados sobre los válidos.

Contrato de salida (docs/contratos_modulos.md):
    {"registros_validos": [], "registros_invalidos": [], "errores": [], "resumen": {}}

Cada registro de entrada termina en UNA sola de las tres listas:
    len(validos) + len(invalidos) + len(errores) == len(registros)
"""
from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
# REVISIÓN (B-2): se importan las funciones del Rol A. Antes el procesamiento
# tenía su propia lista de valores "malos" (N/D, ERROR, SIN_DATO, ...) y su
# propia conversión, es decir, duplicaba la validación. La regla del proyecto es
# no duplicar lógica: la calidad del dato la decide SOLO el Rol A.
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro
from src.exceptions.errores import (
    DataLabError,
    ErrorConversion,
    ErrorEstructuraRegistro,
    ErrorEventoSensor,
    ErrorFormatoFuente,
    EVENTOS_TECNICOS,
    crear_reporte_error,
)

ORIGEN_LOTE = "procesamiento_lote"
PREFIJO_EVENTO = "SIMULACION_"


def _resultado_vacio(errores=None):
    """Resultado con el contrato completo y sin registros.

    # REVISIÓN (B-8): quien consume el resultado (servicio, Streamlit) siempre
    # encuentra las cuatro claves, incluso cuando falla el lote completo.
    """
    return {
        "registros_validos": [],
        "registros_invalidos": [],
        "errores": errores or [],
        "resumen": generar_resumen([]),
    }


def _revisar_eventos_tecnicos(registro):
    """Lanza una excepción si el registro tiene un problema TÉCNICO.

    # REVISIÓN (B-3): antes estos casos terminaban como registros válidos.
    # - Un elemento que no es diccionario no se puede procesar.
    # - `_error_tecnico` es la marca que pone el lector (Rol C) cuando una fila
    #   del archivo viene rota (columnas de más o de menos).
    # - `observacion_tecnica` con SIMULACION_* es un evento del sensor.
    """
    if not isinstance(registro, dict):
        raise ErrorEstructuraRegistro(
            f"El registro no es un diccionario (llegó {type(registro).__name__}: {registro!r})"
        )

    if registro.get("_error_tecnico"):
        fila = registro.get("_fila", "?")
        raise ErrorEstructuraRegistro(f"Fila {fila}: {registro['_error_tecnico']}")

    evento = registro.get("observacion_tecnica")
    if isinstance(evento, str) and evento.strip().upper().startswith(PREFIJO_EVENTO):
        codigo = evento.strip().upper()
        # .get(codigo, ErrorEventoSensor): un evento desconocido usa la clase general.
        clase_error = EVENTOS_TECNICOS.get(codigo, ErrorEventoSensor)
        raise clase_error(f"Evento técnico del sensor: {codigo}")


def _convertir_valor(valor):
    """Convierte el valor a float o lanza ErrorConversion.

    # REVISIÓN (B-8): `raise ... from exc` conserva el error original como causa
    # (se ve en el traceback como "The above exception was the direct cause").
    """
    try:
        return float(valor)
    except (TypeError, ValueError) as exc:
        raise ErrorConversion(f"No se pudo convertir el valor a número: {valor!r}") from exc


def procesar_registros(registros):
    """Procesa un lote de registros de manera robusta, aislando errores individuales."""
    # REVISIÓN (B-8): control de la entrada completa. Si no es una lista no hay
    # registros que recorrer; se informa con el contrato completo.
    if not isinstance(registros, list):
        error = ErrorFormatoFuente(
            f"Se esperaba una lista de registros y llegó {type(registros).__name__}"
        )
        return _resultado_vacio([crear_reporte_error(ORIGEN_LOTE, "N/A", error)])

    # REVISIÓN (B-1): nombres alineados con el contrato.
    validos = []
    invalidos = []
    errores = []

    for registro in registros:
        # REVISIÓN (B-4): identificador y origen se calculan ANTES del try y de
        # forma segura. Antes, si el registro era None o un texto, `reg.get(...)`
        # fallaba dentro del try y OTRA VEZ dentro del except; una excepción
        # lanzada en un bloque except no la captura nadie y el lote se detenía.
        es_dict = isinstance(registro, dict)
        identificador = registro.get("id", "N/A") if es_dict else "N/A"
        origen = registro.get("_origen", ORIGEN_LOTE) if es_dict else ORIGEN_LOTE

        # Trabajo del estudiante: try/except POR REGISTRO. Un error individual
        # no detiene el lote; se registra y se continúa con el siguiente.
        try:
            # 1. Revisión técnica (Rol B).
            _revisar_eventos_tecnicos(registro)

            # 2 y 3. Normalización y validación (Rol A).
            normalizado = normalizar_registro(registro)
            es_valido, motivos = validar_registro(normalizado)

            if not es_valido:
                # REVISIÓN (B-1): antes los motivos se metían DENTRO del registro
                # y además los datos de mala calidad iban a `errores`. La
                # interfaz lee item["registro"] e item["motivos"]; con el
                # formato anterior la pestaña fallaba con KeyError: 'registro'.
                # Se separa "lo que dijo el sensor" de "lo que dijo la revisión".
                invalidos.append({"registro": normalizado, "motivos": motivos})
                # `continue` salta al siguiente registro y ahorra un nivel de else.
                continue

            # 4. Conversión (Rol B).
            valor = _convertir_valor(normalizado["valor"])

            # 5. Clasificación centralizada: se reutiliza, no se duplica.
            # REVISIÓN (B-6): antes se construía un diccionario nuevo con solo
            # id/tipo/valor/unidad y se perdían `fecha` y los metadatos de
            # origen. La interfaz usa `fecha` para la serie temporal; por eso se
            # parte de la copia normalizada completa.
            procesado = dict(normalizado)
            procesado["valor"] = valor
            procesado["clasificacion"] = clasificar_valor(valor, normalizado["tipo"])
            validos.append(procesado)

        # REVISIÓN (B-5): dos bloques except, en este orden:
        #  1. DataLabError: errores PREVISTOS. Cada excepción trae su CATEGORIA,
        #     así que no hace falta una cadena de if/elif.
        #  2. Exception: red de seguridad para lo IMPREVISTO. Va de último porque
        #     Python usa el primer except que coincida, y Exception coincide
        #     con casi todo.
        except DataLabError as error:
            errores.append(crear_reporte_error(origen, identificador, error, error.CATEGORIA))
        except Exception as error:
            errores.append(crear_reporte_error(
                origen, identificador, f"Error inesperado: {type(error).__name__}: {error}", "SISTEMA"
            ))

    # 6. Resumen sobre los registros válidos.
    # REVISIÓN (B-1): faltaba la clave `resumen` del contrato.
    return {
        "registros_validos": validos,
        "registros_invalidos": invalidos,
        "errores": errores,
        "resumen": generar_resumen(validos),
    }
