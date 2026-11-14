"""Rol A: reglas de validación de calidad de registros.

Contrato: validar_registro(registro) -> tuple[bool, list[str]]
La validación devuelve TODOS los motivos encontrados, no solo el primero.
Se espera recibir un registro ya normalizado (normalizar_registro).

# REVISIÓN (general): el archivo tenía dos docstrings y TIPOS_PERMITIDOS
# definido dos veces. Una constante duplicada es una fuente de errores: si
# alguien cambia una copia y no la otra, el programa usa la última sin avisar.
"""
import math

# REVISIÓN: se eliminó `import pandas as pd`; validar un registro no lo requiere.

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}

# REVISIÓN (A-5): antes cada tipo aceptaba varias escrituras ({"°C", "C", "°c",
# "c"}). Ahora la normalización lleva cada unidad a su forma oficial, así que
# aquí basta con UNA unidad por tipo. Cada regla vive en un solo lugar:
# las variantes en normalizacion.py, la unidad oficial aquí.
UNIDADES_PERMITIDAS = {
    "temperatura": "°C",
    "presion": "hPa",
    "humedad": "%",
}

# REVISIÓN (A-4): rangos plausibles por tipo de sensor. Un 999 °C o un 150 % de
# humedad es un número bien escrito, pero no es una medición creíble: antes se
# aceptaban y se clasificaban como ALTO/BAJO, distorsionando el resumen.
# Los rangos salen del análisis de los datasets: las lecturas normales están
# entre 2 y 42 °C, entre 851 y 1080 hPa y entre 5 y 95 %; todos los valores
# extremos intencionales (999, -25, 1500, 150, ...) quedan fuera.
# No son estándares reales: son reglas pedagógicas para datos sintéticos.
# IMPORTANTE: validar un rango NO es clasificar. BAJO/NORMAL/ALTO sigue
# centralizado en src/processing/clasificacion.py.
RANGOS_PLAUSIBLES = {
    "temperatura": (-10.0, 50.0),
    "presion": (800.0, 1100.0),
    "humedad": (0.0, 100.0),
}

CAMPOS_OBLIGATORIOS = ("id", "tipo", "valor", "unidad")


def esta_vacio(contenido) -> bool:
    """Indica si un campo no tiene dato: None, texto vacío o NaN.

    # REVISIÓN (A-3): antes NaN no se consideraba vacío; una celda vacía de
    # Excel producía "no numérico: nan" mientras que la misma celda en CSV
    # producía "campo faltante". La validación no debe depender del origen.
    """
    if contenido is None:
        return True
    if isinstance(contenido, str) and contenido.strip() == "":
        return True
    # NaN es el único valor distinto de sí mismo.
    if isinstance(contenido, float) and contenido != contenido:
        return True
    return False


def convertir_a_numero(valor):
    """Devuelve el valor como float si es un número válido y finito; si no, None.

    # REVISIÓN (A-3): casos que suelen pasar inadvertidos:
    #  - True/False: en Python bool es subclase de int (float(True) == 1.0).
    #  - "nan", "inf": float() los acepta, pero no son mediciones.
    """
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        numero = float(valor)
    elif isinstance(valor, str):
        try:
            numero = float(valor)
        except ValueError:
            return None
    else:
        return None
    if not math.isfinite(numero):
        return None
    return numero


def validar_registro(registro: dict) -> tuple[bool, list[str]]:
    """Valida un registro normalizado y devuelve (es_valido, motivos)."""
    motivos = []

    # REVISIÓN: si no es un diccionario no se puede validar campo a campo.
    # Se devuelve un motivo en lugar de lanzar una excepción: una validación
    # responde "sí/no y por qué"; no detiene el programa.
    if not isinstance(registro, dict):
        return False, ["Estructura no válida: el registro no es un diccionario"]

    # Trabajo del estudiante: revisión de campos obligatorios.
    # REVISIÓN (A-2): antes, si faltaba un campo, la función hacía `return`
    # inmediatamente y no revisaba los demás campos. El contrato pide devolver
    # TODOS los motivos. Ahora se anotan los campos faltantes y se sigue
    # revisando los que sí existen.
    faltantes = set()
    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in registro or esta_vacio(registro[campo]):
            faltantes.add(campo)
            # REVISIÓN (A-7): mensaje con el formato "Categoría: detalle".
            # La interfaz agrupa los motivos por el texto anterior a ":", así
            # que todos los faltantes de "valor" quedan en una misma barra.
            motivos.append(f"Campo obligatorio faltante: {campo}")

    tipo = registro.get("tipo")
    unidad = registro.get("unidad")
    valor = registro.get("valor")

    # Tipo permitido.
    # REVISIÓN (A-8): isinstance(tipo, str) antes de buscar en el set. Un set
    # solo puede buscar elementos hashables; `["x"] in set` lanza TypeError.
    # El operador `and` evalúa en cortocircuito: si la primera condición es
    # falsa, la segunda no se ejecuta.
    tipo_es_conocido = isinstance(tipo, str) and tipo in TIPOS_PERMITIDOS
    if "tipo" not in faltantes and not tipo_es_conocido:
        motivos.append(
            f"Tipo no permitido: '{tipo}' (permitidos: {', '.join(sorted(TIPOS_PERMITIDOS))})"
        )

    # Unidad válida para el tipo.
    # Trabajo del estudiante: la unidad solo se revisa si el tipo es conocido.
    # Es correcto: si el tipo es desconocido no se sabe qué unidad corresponde,
    # y el motivo "Tipo no permitido" ya explica el rechazo.
    # REVISIÓN (A-7): el mensaje indica cuál unidad se esperaba.
    if "unidad" not in faltantes and tipo_es_conocido:
        esperada = UNIDADES_PERMITIDAS[tipo]
        if unidad != esperada:
            motivos.append(f"Unidad no válida: '{unidad}' (se esperaba '{esperada}' para {tipo})")

    # Formato numérico y rango plausible.
    if "valor" not in faltantes:
        numero = convertir_a_numero(valor)
        if numero is None:
            # Trabajo del estudiante: motivo de valor no numérico, con el valor
            # recibido entre comillas para que se vea qué llegó.
            motivos.append(f"Valor no numérico: '{valor}'")
        elif tipo_es_conocido:
            # REVISIÓN (A-4): rango plausible (credibilidad del dato).
            minimo, maximo = RANGOS_PLAUSIBLES[tipo]
            if numero < minimo or numero > maximo:
                motivos.append(
                    f"Valor fuera de rango plausible: {numero:g} "
                    f"(para {tipo} se acepta de {minimo:g} a {maximo:g} {UNIDADES_PERMITIDAS[tipo]})"
                )

    es_valido = len(motivos) == 0
    return es_valido, motivos


# REVISIÓN (A-1): se eliminó el bloque final que leía
# "C:\Repositorio\...\data\processed\temperatura_limpio.csv" y escribía los
# archivos de válidos y rechazados. Se ejecutaba en cada `import` y rompía la
# aplicación en cualquier equipo distinto al del estudiante. Separar válidos e
# inválidos de un lote es tarea de procesar_registros (Rol B).
if __name__ == "__main__":
    print(validar_registro({"id": "T1", "tipo": "temperatura", "valor": "999", "unidad": "°C"}))
    print(validar_registro({"id": "", "tipo": "otro", "valor": "x", "unidad": ""}))
