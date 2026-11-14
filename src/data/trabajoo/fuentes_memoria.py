
from copy import deepcopy


class FuenteMemoria:
    """Adaptador para entregar registros almacenados en memoria."""

    def __init__(self, registros):
        self.registros = deepcopy(registros)

    def leer(self):
        """Devuelve una copia de los registros."""
        return deepcopy(self.registros)


def crear_fuente_prueba():
    """Crea un conjunto de registros de prueba."""

    registros = [
        {
            "id": 1,
            "tipo": "temperatura",
            "valor": 25.5,
            "unidad": "°C"
        },
        {
            "id": 2,
            "tipo": "presion",
            "valor": 101.3,
            "unidad": "kPa"
        },
        {
            "id": 3,
            "tipo": "humedad",
            "valor": 65,
            "unidad": "%"
        }
    ]

    return FuenteMemoria(registros)


def crear_fuente_defectuosa():
    """Crea registros con diferentes problemas para realizar pruebas."""

    registros = [
        {
            "id": 1,
            "tipo": "temperatura",
            "valor": 25.5,
            "unidad": "°C"
        },
        {
            "id": 2,
            "tipo": "temperatura",
            "valor": None,
            "unidad": "°C"
        },
        {
            "id": 3,
            "tipo": "presion",
            "valor": "dato incorrecto",
            "unidad": "kPa"
        },
        {
            "id": 4,
            "tipo": "humedad",
            "valor": 150,
            "unidad": "%"
        },
        {
            "id": 5,
            "tipo": "humedad",
            "valor": 60,
            "unidad": "%"
        }
    ]

    return FuenteMemoria(registros)
