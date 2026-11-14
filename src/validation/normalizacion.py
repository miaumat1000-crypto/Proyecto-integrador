"""Rol A: normalización y estandarización de registros.

Contrato: recibir un diccionario y devolver una COPIA normalizada.
No modificar el registro original.

# REVISIÓN (general): el archivo tenía dos docstrings seguidos. Solo el primero
# es la documentación del módulo; el segundo era una cadena suelta sin efecto.
# Se dejó uno solo.
"""

# REVISIÓN (A-5): se eliminó `import pandas as pd`. La normalización trabaja con
# un diccionario a la vez y no necesita pandas. Menos dependencias = módulo más
# fácil de probar y de importar desde cualquier capa.


# REVISIÓN (A-5): tabla de equivalencias de unidades. Antes la unidad solo se
# limpiaba con strip(), así que "HPA" o "°c" llegaban a la validación tal cual y
# se rechazaban aunque fueran la misma unidad mal escrita.
# Una tabla (diccionario) reemplaza muchos `if`: para aceptar una variante nueva
# basta con agregar una línea. Las claves están en minúsculas y sin espacios.
EQUIVALENCIAS_UNIDAD = {
    "°c": "°C",
    "ºc": "°C",   # el carácter "º" (ordinal) se confunde a menudo con "°" (grado)
    "c": "°C",
    "celsius": "°C",
    "hpa": "hPa",
    "hectopascal": "hPa",
    "hectopascales": "hPa",
    "%": "%",
    "porcentaje": "%",
}

# REVISIÓN (A-6): tabla para quitar tildes. "Presión" se convertía en "presión",
# que no coincide con "presion" en TIPOS_PERMITIDOS. str.maketrans + translate
# cambian varios caracteres en una sola pasada.
SIN_TILDES = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")

# Campos de texto a los que se les quitan los espacios de los extremos.
CAMPOS_A_LIMPIAR = ("id", "tipo", "unidad", "valor")


def _es_nan(valor):
    """Devuelve True si el valor es un NaN (por ejemplo, una celda vacía de pandas).

    # REVISIÓN (A-3): NaN es el único valor que es distinto de sí mismo, por eso
    # `valor != valor` lo detecta sin necesidad de importar math ni pandas.
    """
    return isinstance(valor, float) and valor != valor


def normalizar_registro(registro: dict) -> dict:
    """Devuelve una copia del registro con id, tipo, unidad y valor estandarizados.

    - id: sin espacios y en MAYÚSCULAS ("p101" y "P101" son el mismo sensor).
    - tipo: sin espacios, en minúsculas y sin tildes ("Presión" -> "presion").
    - unidad: sin espacios y llevada a su forma oficial ("HPA" -> "hPa").
    - valor: si es texto, sin espacios y con coma decimal convertida a punto.
      El valor NO se convierte a número aquí: convertir y decidir si es válido
      corresponde a la validación (Rol A) y al procesamiento (Rol B).
    """
    # Trabajo del estudiante: se conserva la verificación de tipo de entrada.
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")

    # Trabajo del estudiante: copia superficial, el original no se modifica.
    copia = registro.copy()

    # REVISIÓN (A-3): un NaN (celda vacía de Excel/pandas) se convierte en None
    # para que la validación lo reporte como "campo faltante", igual que un
    # vacío de CSV o JSON. Es una defensa en profundidad: aunque el Rol C ya
    # evita los NaN, la calidad no debe depender del origen de los datos.
    for campo in CAMPOS_A_LIMPIAR:
        if campo in copia and _es_nan(copia[campo]):
            copia[campo] = None

    # Trabajo del estudiante: strip() de los campos de texto.
    # REVISIÓN: se unificó en un solo ciclo (antes "valor" se limpiaba aparte).
    for campo in CAMPOS_A_LIMPIAR:
        if campo in copia and isinstance(copia[campo], str):
            copia[campo] = copia[campo].strip()

    # REVISIÓN (A-6): el id se pasa a mayúsculas. Se revisa isinstance antes de
    # llamar a .upper(): un id numérico (por ejemplo 101) no tiene ese método.
    if "id" in copia and isinstance(copia["id"], str):
        copia["id"] = copia["id"].upper()

    # Trabajo del estudiante: tipo en minúsculas.
    # REVISIÓN (A-6): además se quitan las tildes.
    if "tipo" in copia and isinstance(copia["tipo"], str):
        copia["tipo"] = copia["tipo"].lower().translate(SIN_TILDES)

    # REVISIÓN (A-5): estandarización de la unidad con la tabla de equivalencias.
    # Si la unidad no está en la tabla se deja tal como llegó: normalizar no es
    # aceptar cualquier cosa; la validación explicará por qué se rechaza.
    if "unidad" in copia and isinstance(copia["unidad"], str):
        clave = copia["unidad"].lower().replace(" ", "")
        copia["unidad"] = EQUIVALENCIAS_UNIDAD.get(clave, copia["unidad"])

    # REVISIÓN (A-9): coma decimal en valores de texto ("21,5" -> "21.5").
    # La regla es conservadora: solo actúa si hay exactamente una coma y ningún
    # punto. "1.013,2" se deja igual y la validación lo rechaza; normalizar no
    # debe inventar datos.
    if "valor" in copia and isinstance(copia["valor"], str):
        texto = copia["valor"]
        if texto.count(",") == 1 and "." not in texto:
            copia["valor"] = texto.replace(",", ".")

    return copia


# REVISIÓN (A-1): se eliminó el bloque que estaba al final del archivo y que
# leía "C:\Repositorio\Proyecto-integrador\data\raw\temperatura.csv" y escribía
# en data/processed.
#  1. Todo lo que está en el nivel superior de un módulo se ejecuta al hacer
#     `import`. Por eso, al importar este archivo desde Streamlit, el servicio o
#     las pruebas, se intentaba abrir un archivo en una ruta de Windows que no
#     existe en otros equipos y la aplicación completa fallaba con
#     FileNotFoundError.
#  2. Leer archivos es responsabilidad del Rol C (lectores.py) y recorrer el lote
#     es responsabilidad del Rol B (procesamiento.py). Este módulo solo
#     normaliza UN registro.
# Para hacer una prueba manual se usa el bloque `if __name__ == "__main__":`,
# que solo se ejecuta cuando se corre el archivo directamente:
#     python -m src.validation.normalizacion
if __name__ == "__main__":
    ejemplo = {"id": " p101 ", "tipo": " Presión ", "valor": " 1013,2 ", "unidad": " HPA "}
    print("Original:   ", ejemplo)
    print("Normalizado:", normalizar_registro(ejemplo))
