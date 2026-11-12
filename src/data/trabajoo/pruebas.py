
import json
import pytest

from src.data.fuentes_memoria import (
    FuenteMemoria,
    crear_fuente_prueba,
    crear_fuente_defectuosa
)

from src.data.carga_datos import (
    cargar_datos,
    cargar_desde_memoria
)


def test_fuente_memoria():
    fuente = crear_fuente_prueba()

    registros = fuente.leer()

    assert len(registros) == 3
    assert registros[0]["tipo"] == "temperatura"


def test_copia_de_registros():
    fuente = crear_fuente_prueba()

    registros = fuente.leer()
    registros[0]["valor"] = 999

    assert fuente.leer()[0]["valor"] == 25.5


def test_fuente_defectuosa():
    fuente = crear_fuente_defectuosa()

    registros = fuente.leer()

    assert len(registros) == 5
    assert registros[1]["valor"] is None
    assert registros[2]["valor"] == "dato incorrecto"


def test_carga_memoria():
    fuente = crear_fuente_prueba()

    registros = cargar_desde_memoria(fuente)

    assert len(registros) == 3


def test_csv(tmp_path):
    archivo = tmp_path / "sensores.csv"

    archivo.write_text(
        "id,tipo,valor,unidad\n"
        "1,temperatura,25.5,C\n",
        encoding="utf-8"
    )

    registros = cargar_datos(archivo)

    assert len(registros) == 1
    assert registros[0]["tipo"] == "temperatura"


def test_json(tmp_path):
    archivo = tmp_path / "sensores.json"

    datos = [
        {
            "id": 1,
            "tipo": "presion",
            "valor": 101.3,
            "unidad": "kPa"
        }
    ]

    archivo.write_text(
        json.dumps(datos),
        encoding="utf-8"
    )

    registros = cargar_datos(archivo)

    assert len(registros) == 1
    assert registros[0]["tipo"] == "presion"


def test_archivo_inexistente():
    with pytest.raises(FileNotFoundError):
        cargar_datos("archivo_inexistente.csv")


def test_formato_no_compatible(tmp_path):
    archivo = tmp_path / "datos.txt"
    archivo.write_text("datos", encoding="utf-8")

    with pytest.raises(ValueError):
        cargar_datos(archivo)


def test_fuente_invalida():
    fuente = FuenteMemoria({"dato": "incorrecto"})

    with pytest.raises(TypeError):
        cargar_desde_memoria(fuente)
