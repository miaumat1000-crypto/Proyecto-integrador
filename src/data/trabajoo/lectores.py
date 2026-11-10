"""Rol C: lectores de archivos. Implementación del estudiante en semana 12.

Contrato de salida para cada lector: list[dict] con claves id, tipo, valor, unidad.
Los lectores no normalizan ni clasifican: entregan datos crudos al servicio.
"""
import csv
import json
import pandas as pd

def leer_csv(archivo):
    # TODO C-S12-01: leer CSV y devolver lista de diccionarios.
    registros = []
    # Suponiendo que 'archivo' puede ser un ruta o un objeto abierto en modo lectura
    if isinstance(archivo, str):
        with open(archivo, mode="r", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                registros.append(dict(fila))
    else:
        # Si es un objeto de archivo abierto o stream
        lector = csv.DictReader(archivo)
        for fila in lector:
            registros.append(dict(fila))
    return registros

def leer_json(archivo):
    # TODO C-S12-02: leer JSON y devolver lista de diccionarios.
    if isinstance(archivo, str):
        with open(archivo, mode="r", encoding="utf-8") as f:
            datos = json.load(f)
    else:
        datos = json.load(archivo)
    
    # Asegurar que devuelva una lista de diccionarios
    if isinstance(datos, dict):
        return [datos]
    return datos

def leer_excel(archivo):
    # TODO C-S12-03: leer Excel y devolver lista de diccionarios.
    # Usando pandas para leer el archivo Excel de manera sencilla
    df = pd.read_excel(archivo)
    # Remplazar valores NaN por strings vacíos o None para evitar errores de tipo
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")