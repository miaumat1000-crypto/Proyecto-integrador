"""Rol A: normalización y estandarización de registros.

SEMANA 10: implementar las funciones marcadas TODO.
Contrato: recibir un diccionario y devolver una COPIA normalizada.
No modificar el registro original.
"""
"""Rol A: normalización y estandarización de registros."""


import pandas as pd


def normalizar_registro(registro: dict) -> dict:
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")

    copia = registro.copy()

    for clave in ("id", "tipo", "unidad"):
        if clave in copia and isinstance(copia[clave], str):
            copia[clave] = copia[clave].strip()

    if "tipo" in copia and isinstance(copia["tipo"], str):
        copia["tipo"] = copia["tipo"].lower()

    if "valor" in copia and isinstance(copia["valor"], str):
        copia["valor"] = copia["valor"].strip()

    return copia


# 1. Cargar el archivo CSV
ruta_entrada = r"C:\Repositorio\Proyecto-integrador\data\raw\temperatura.csv"
df = pd.read_csv(ruta_entrada)

# 2. Convertir las filas a diccionarios y aplicar la función
registros_normalizados = [
    normalizar_registro(row) for row in df.to_dict(orient="records")
]

# 3. Reconstruir el DataFrame normalizado
df_normalizado = pd.DataFrame(registros_normalizados)

# 4. Guardar los resultados (puedes sobrescribir o guardar en /processed/)
ruta_salida = (
    r"C:\Repositorio\Proyecto-integrador\data\processed\temperatura_limpio.csv"
)
df_normalizado.to_csv(ruta_salida, index=False)

print(f"Archivo procesado exitosamente y guardado en: {ruta_salida}")