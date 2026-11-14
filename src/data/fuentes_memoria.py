"""Rol C: adaptador de fuentes en memoria y escenarios de prueba.

Contenido:
    cargar_desde_memoria(fuente=None)   -> 12 registros base (o los de una FuenteMemoria)
    FuenteMemoria                       -> adaptador del estudiante (src/data/trabajoo)
    preparar_registros_prueba()         -> semana 10: datos de MALA CALIDAD (los rechaza el Rol A)
    preparar_escenarios_defectuosos()   -> semana 11: FUENTES DEFECTUOSAS (las reporta el Rol B)

# REVISIÓN (C-1): este archivo seguía con el TODO original y NotImplementedError,
# mientras que el trabajo del rol estaba en src/data/trabajoo/fuentes_memoria.py,
# una carpeta que la aplicación nunca importaba. Se trasladó aquí, que es el
# archivo que define el contrato, y se eliminó la carpeta `trabajoo`. Las
# versiones originales siguen disponibles en el historial de Git (commit 26fe724).
"""
from copy import deepcopy

from src.data.sensores import obtener_registros
from src.exceptions.errores import ErrorFormatoFuente


# ---------------------------------------------------------------------------
# Adaptador en memoria (trabajo del estudiante, trasladado desde trabajoo/)
# ---------------------------------------------------------------------------
class FuenteMemoria:
    """Adaptador para entregar registros almacenados en memoria.

    Trabajo del estudiante: guarda una copia profunda (deepcopy) y entrega otra
    copia en cada lectura, de modo que quien la usa no puede alterar la fuente.
    """

    def __init__(self, registros):
        self.registros = deepcopy(registros)

    def leer(self):
        """Devuelve una copia de los registros."""
        return deepcopy(self.registros)


def cargar_desde_memoria(fuente=None):
    """Fuente de datos funcional desde la primera entrega.

    - Sin argumentos: devuelve los 12 registros base (contrato del servicio:
      `cargar_datos()` llama a `cargar_desde_memoria()` sin parámetros).
    - Con una FuenteMemoria: devuelve sus registros.

    # REVISIÓN (C-2): el estudiante definió `cargar_desde_memoria(fuente)` en
    # carga_datos.py con un parámetro OBLIGATORIO. El servicio docente y la
    # demostración la llaman sin argumentos, así que habría fallado con
    # TypeError. Con `fuente=None` se aceptan las dos formas sin romper el
    # contrato. Además, dos funciones con el mismo nombre en módulos distintos
    # confunden: ahora existe una sola.
    """
    if fuente is None:
        return obtener_registros()

    registros = fuente.leer()
    # Trabajo del estudiante: verificación de que la fuente devuelve una lista.
    # REVISIÓN (C-5): se usa la excepción del contrato en vez de TypeError.
    if not isinstance(registros, list):
        raise ErrorFormatoFuente("La fuente de memoria debe devolver una lista.")
    return registros


# ---------------------------------------------------------------------------
# Fuentes de prueba del estudiante (trasladadas desde trabajoo/)
# ---------------------------------------------------------------------------
def crear_fuente_prueba():
    """Crea un conjunto pequeño de registros de prueba (trabajo del estudiante).

    Nota de revisión: el registro de presión usa 101.3 kPa. Es un buen caso de
    prueba: la unidad oficial del proyecto es hPa (1013 hPa = 101.3 kPa), así
    que el Rol A lo rechaza por unidad no válida.
    """
    registros = [
        {"id": 1, "tipo": "temperatura", "valor": 25.5, "unidad": "°C"},
        {"id": 2, "tipo": "presion", "valor": 101.3, "unidad": "kPa"},
        {"id": 3, "tipo": "humedad", "valor": 65, "unidad": "%"},
    ]
    return FuenteMemoria(registros)


def crear_fuente_defectuosa():
    """Crea registros con problemas de CALIDAD (trabajo del estudiante).

    Nota de revisión: estos registros tienen datos de mala calidad (valor None,
    texto, 150 % de humedad). Los rechaza el Rol A y van a `registros_invalidos`.
    No confundir con preparar_escenarios_defectuosos(), que simula fallas del
    ORIGEN y van a `errores`.
    """
    registros = [
        {"id": 1, "tipo": "temperatura", "valor": 25.5, "unidad": "°C"},
        {"id": 2, "tipo": "temperatura", "valor": None, "unidad": "°C"},
        {"id": 3, "tipo": "presion", "valor": "dato incorrecto", "unidad": "kPa"},
        {"id": 4, "tipo": "humedad", "valor": 150, "unidad": "%"},
        {"id": 5, "tipo": "humedad", "valor": 60, "unidad": "%"},
    ]
    return FuenteMemoria(registros)


# ---------------------------------------------------------------------------
# Semana 10 — escenarios de entrada con formatos variados
# ---------------------------------------------------------------------------
def preparar_registros_prueba():
    """Registros base + variantes de formato + casos incompletos y no reconocidos.

    # REVISIÓN (C-4): faltaba esta función (TODO C-S10-01 a C-S10-03) y la
    # prueba del docente `test_lote_continua_y_separa_resultados` la usa.
    # Los registros nuevos usan ids de la serie 1xx para distinguirlos.
    """
    # TODO C-S10-03: no alterar los 12 registros base -> se parte de una copia.
    registros = deepcopy(cargar_desde_memoria())

    # TODO C-S10-01: espacios, mayúsculas y formatos diversos.
    # Todos deberían quedar VÁLIDOS después de la normalización del Rol A.
    registros += [
        {"id": " t101 ", "tipo": " TEMPERATURA ", "valor": " 21.5 ", "unidad": " °C "},
        {"id": "T102", "tipo": "Temperatura", "valor": "19,8", "unidad": "C"},
        {"id": "p101", "tipo": "Presión", "valor": "1013.2", "unidad": "HPA"},
        {"id": "H101", "tipo": "HUMEDAD", "valor": 45, "unidad": " % "},
    ]

    # TODO C-S10-02: casos incompletos y tipos no reconocidos.
    # Todos deberían quedar INVÁLIDOS, con sus motivos.
    registros += [
        {"id": "T103", "tipo": "temperatura", "valor": "", "unidad": "°C"},         # valor vacío
        {"id": "T104", "tipo": "temperatura", "unidad": "°C"},                      # falta "valor"
        {"id": "", "tipo": "humedad", "valor": 50, "unidad": "%"},                  # id vacío
        {"id": "X101", "tipo": "viento", "valor": 12, "unidad": "km/h"},            # tipo no reconocido
        {"id": "P102", "tipo": "presion", "valor": "N/A", "unidad": "hPa"},         # no numérico
        {"id": "H102", "tipo": "humedad", "valor": 150, "unidad": "%"},             # fuera de rango
    ]

    # Se aprovechan las fuentes que construyó el estudiante.
    registros += crear_fuente_prueba().leer()
    return registros


# ---------------------------------------------------------------------------
# Semana 11 — escenarios de fuentes defectuosas
# ---------------------------------------------------------------------------
def preparar_escenarios_defectuosos():
    """Simula fallas del ORIGEN de datos (no de calidad del dato).

    # REVISIÓN (C-6): faltaba el entregable de la semana 11 del Rol C
    # ("escenarios de fuentes defectuosas"). Resultado esperado al procesar:
    # 2 válidos y 4 errores técnicos; el lote no se detiene.
    """
    return [
        {"id": "T201", "tipo": "temperatura", "valor": 22.0, "unidad": "°C"},
        # Evento técnico del sensor -> ErrorTimeoutSensor
        {"id": "T202", "tipo": "temperatura", "valor": 23.0, "unidad": "°C",
         "observacion_tecnica": "SIMULACION_TIMEOUT_SENSOR"},
        # Fila irregular marcada por un lector -> ErrorEstructuraRegistro
        {"id": "P201", "_error_tecnico": "la fila tiene 7 columnas y se esperaban 6",
         "_origen": "escenario.csv", "_fila": 4},
        # Un elemento que no es diccionario -> ErrorEstructuraRegistro
        "T203;temperatura;24;°C",
        # Elemento vacío -> ErrorEstructuraRegistro
        None,
        {"id": "H201", "tipo": "humedad", "valor": 55.0, "unidad": "%"},
    ]


# REVISIÓN: prueba manual. Todo lo que está en el nivel superior de un módulo
# se ejecuta al importarlo; por eso las pruebas rápidas van dentro de
# `if __name__ == "__main__":`, que solo corre al ejecutar el archivo:
#     python -m src.data.fuentes_memoria
if __name__ == "__main__":
    print("Base:", len(cargar_desde_memoria()))
    print("Prueba S10:", len(preparar_registros_prueba()))
    print("Defectuosos S11:", len(preparar_escenarios_defectuosos()))
