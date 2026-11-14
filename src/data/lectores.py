"""Rol C: lectores de archivos (semana 12).

Contrato de salida para cada lector: list[dict] con claves id, tipo, valor, unidad
(y las columnas adicionales del archivo, como fecha y observacion_tecnica).
Los lectores NO normalizan, NO validan y NO clasifican: entregan los datos tal
como están en el archivo.

Cada lector acepta:
    - una ruta (str o Path)                  -> uso desde consola o pruebas
    - bytes                                  -> contenido ya leído
    - un objeto con .getvalue() o .read()    -> archivo subido en Streamlit (UploadedFile/BytesIO)

Metadatos de trazabilidad que agregan los lectores a cada registro:
    _origen: nombre del archivo
    _fila:   número de fila en el archivo (o posición en el JSON)
    _error_tecnico: solo si la fila está rota; el Rol B la reporta como error.

# REVISIÓN (C-1): este archivo seguía con los TODO originales. El trabajo del
# estudiante estaba en src/data/trabajoo/Lectore.py, que la aplicación no
# importaba. Se trasladó aquí conservando sus decisiones (utf-8-sig, JSON con
# clave "registros", Excel con openpyxl, encabezados vacíos o duplicados) y se
# adaptó al contrato.
"""
# REVISIÓN (C-1): PEP 8 indica que todas las importaciones van al inicio del
# archivo, agrupadas: biblioteca estándar, terceros y proyecto.
import csv
import io
import json
from pathlib import Path

from src.exceptions.errores import ErrorFormatoFuente, ErrorLecturaFuente

COLUMNAS_REQUERIDAS = ("id", "tipo", "valor", "unidad")


# ---------------------------------------------------------------------------
# Utilidades comunes a los tres lectores
# ---------------------------------------------------------------------------
def _obtener_bytes(archivo):
    """Convierte cualquier entrada aceptada en bytes.

    # REVISIÓN (C-3): el lector del estudiante hacía Path(ruta).open(...), que
    # solo funciona con rutas. Streamlit entrega un objeto UploadedFile (parecido
    # a un archivo abierto) y el servicio llama cargar_datos(archivo, nombre):
    # con una ruta se esperaba str y llegaba un objeto -> TypeError.
    # Patrón ADAPTADOR: esta función convierte cualquier entrada a bytes y los
    # tres lectores trabajan siempre sobre el mismo tipo.
    # `hasattr` permite aceptar "cualquier cosa que tenga .read()" sin conocer
    # su clase (duck typing).
    """
    try:
        if isinstance(archivo, (str, Path)):
            return Path(archivo).read_bytes()
        if isinstance(archivo, (bytes, bytearray)):
            return bytes(archivo)
        if hasattr(archivo, "getvalue"):          # Streamlit UploadedFile / BytesIO
            return archivo.getvalue()
        if hasattr(archivo, "read"):              # archivo abierto en modo binario
            contenido = archivo.read()
            return contenido.encode("utf-8") if isinstance(contenido, str) else contenido
    except OSError as exc:
        # FileNotFoundError, PermissionError, IsADirectoryError... heredan de OSError.
        raise ErrorLecturaFuente(f"No fue posible leer el archivo '{archivo}': {exc}") from exc
    raise ErrorFormatoFuente(f"Tipo de entrada no soportado por los lectores: {type(archivo).__name__}")


def _nombre_de(archivo):
    """Nombre del archivo para la trazabilidad (_origen)."""
    if isinstance(archivo, (str, Path)):
        return Path(archivo).name
    return getattr(archivo, "name", "memoria")


def _decodificar(contenido, nombre):
    """bytes -> texto. utf-8-sig quita el BOM que agrega Excel al guardar CSV."""
    try:
        return contenido.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ErrorLecturaFuente(f"'{nombre}' no está codificado en UTF-8: {exc}") from exc


def _verificar_columnas(encabezados, nombre):
    """Lanza ErrorFormatoFuente si faltan columnas del contrato.

    # REVISIÓN (C-5): sin esta verificación, un archivo con otras columnas se
    # leía "bien" y fallaba más adelante con errores difíciles de entender.
    # Si falta una columna en el ENCABEZADO, el archivo completo no sirve.
    """
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in encabezados]
    if faltantes:
        raise ErrorFormatoFuente(
            f"'{nombre}' no tiene las columnas obligatorias: {', '.join(faltantes)}"
        )


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------
def leer_csv(archivo):
    """Lee un archivo CSV y devuelve una lista de diccionarios."""
    nombre = _nombre_de(archivo)
    texto = _decodificar(_obtener_bytes(archivo), nombre)

    # Trabajo del estudiante: csv.DictReader convierte cada fila en un dict
    # usando el encabezado. Se lee desde io.StringIO porque ya tenemos el texto.
    lector = csv.DictReader(io.StringIO(texto, newline=""))
    if lector.fieldnames is None:
        raise ErrorFormatoFuente(f"'{nombre}' está vacío: no tiene encabezado")
    encabezados = [c.strip() for c in lector.fieldnames]
    lector.fieldnames = encabezados
    _verificar_columnas(encabezados, nombre)

    registros = []
    # La fila 1 es el encabezado; los datos empiezan en la fila 2.
    for numero_fila, fila in enumerate(lector, start=2):
        registro = dict(fila)
        registro["_origen"] = nombre
        registro["_fila"] = numero_fila

        # REVISIÓN (C-5): fila irregular. DictReader guarda las columnas de más
        # bajo la clave None y rellena con None las que faltan. En lugar de
        # lanzar una excepción (que detendría la lectura de las demás filas),
        # la fila se MARCA y el Rol B la reporta como ESTRUCTURA_REGISTRO.
        if None in registro:
            sobrantes = registro.pop(None)
            registro["_error_tecnico"] = (
                f"la fila tiene {len(encabezados) + len(sobrantes)} columnas y se esperaban {len(encabezados)}"
            )
        elif any(registro[c] is None for c in encabezados):
            presentes = sum(1 for c in encabezados if registro[c] is not None)
            registro["_error_tecnico"] = (
                f"la fila tiene {presentes} columnas y se esperaban {len(encabezados)}"
            )
        registros.append(registro)
    return registros


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------
def leer_json(archivo):
    """Lee un archivo JSON y devuelve sus registros.

    Acepta una lista de registros o un objeto {"registros": [...]}
    (este último es el formato de data/raw/presion.json).
    """
    nombre = _nombre_de(archivo)
    texto = _decodificar(_obtener_bytes(archivo), nombre)

    # REVISIÓN (C-5): JSON mal formado -> ErrorLecturaFuente con línea y columna.
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErrorLecturaFuente(
            f"'{nombre}' no es un JSON válido (línea {exc.lineno}, columna {exc.colno}): {exc.msg}"
        ) from exc

    # Trabajo del estudiante: lista directa o clave "registros".
    if isinstance(datos, dict) and isinstance(datos.get("registros"), list):
        datos = datos["registros"]
    if not isinstance(datos, list):
        # REVISIÓN (C-5): ErrorFormatoFuente en vez de ValueError genérico.
        raise ErrorFormatoFuente(
            f"'{nombre}' debe contener una lista de registros o una clave 'registros' con una lista"
        )

    registros = []
    for posicion, elemento in enumerate(datos, start=1):
        if isinstance(elemento, dict):
            registro = dict(elemento)
            registro["_origen"] = nombre
            registro["_fila"] = posicion
            registros.append(registro)
        else:
            # Un elemento que no es diccionario se entrega tal cual: el lector
            # no decide. El Rol B lo reporta como ESTRUCTURA_REGISTRO.
            registros.append(elemento)
    return registros


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------
def leer_excel(archivo, hoja=0):
    """Lee una hoja de Excel (.xlsx) y devuelve una lista de diccionarios.

    Trabajo del estudiante: se usa openpyxl directamente (no pandas). Es una
    buena decisión: openpyxl entrega las celdas vacías como None y el texto
    "NA" como texto, sin convertirlos en NaN como hace pandas por defecto.
    """
    # Import dentro de la función (decisión del estudiante): si openpyxl no está
    # instalado solo falla la lectura de Excel, no el resto de la aplicación.
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise ErrorLecturaFuente("Se necesita instalar openpyxl para leer Excel.") from exc

    nombre = _nombre_de(archivo)
    contenido = _obtener_bytes(archivo)

    # REVISIÓN (C-3): load_workbook acepta un objeto tipo archivo; con
    # io.BytesIO funciona igual para rutas y para archivos de Streamlit.
    # REVISIÓN (C-5): un archivo que no es Excel produce BadZipFile u otros
    # errores internos de openpyxl; se traducen a la excepción del contrato.
    try:
        libro = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    except Exception as exc:
        raise ErrorLecturaFuente(f"'{nombre}' no es un archivo Excel válido: {exc}") from exc

    try:
        # Trabajo del estudiante: selección de hoja por índice o por nombre.
        if isinstance(hoja, int):
            if hoja < 0 or hoja >= len(libro.sheetnames):
                raise ErrorFormatoFuente(f"'{nombre}': el índice de hoja {hoja} no existe.")
            pagina = libro.worksheets[hoja]
        else:
            if hoja not in libro.sheetnames:
                raise ErrorFormatoFuente(f"'{nombre}': no existe la hoja {hoja}.")
            pagina = libro[hoja]

        filas = pagina.iter_rows(values_only=True)
        encabezados = next(filas, None)
        if encabezados is None:
            raise ErrorFormatoFuente(f"'{nombre}' está vacío: no tiene encabezado")

        # Trabajo del estudiante: encabezados vacíos o duplicados.
        # REVISIÓN (C-5): ErrorFormatoFuente en vez de ValueError.
        encabezados = [str(e).strip() if e is not None else "" for e in encabezados]
        if any(e == "" for e in encabezados):
            raise ErrorFormatoFuente(f"'{nombre}' contiene encabezados vacíos.")
        if len(set(encabezados)) != len(encabezados):
            raise ErrorFormatoFuente(f"'{nombre}' contiene encabezados duplicados.")
        _verificar_columnas(encabezados, nombre)

        registros = []
        for numero_fila, fila in enumerate(filas, start=2):
            # Trabajo del estudiante: se omiten las filas completamente vacías.
            if all(valor is None for valor in fila):
                continue
            registro = dict(zip(encabezados, fila))
            # REVISIÓN (C-7): salida homogénea con CSV. En CSV una celda vacía
            # llega como "" y aquí llegaba como None; se iguala para que el
            # mismo dato produzca el mismo registro sin importar el formato.
            for clave, valor in registro.items():
                if valor is None:
                    registro[clave] = ""
            registro["_origen"] = nombre
            registro["_fila"] = numero_fila
            registros.append(registro)
        return registros
    finally:
        # Trabajo del estudiante: cerrar el libro siempre, incluso si hay error.
        libro.close()
