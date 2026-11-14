"""Rol A: reglas de validación de calidad de registros."""
TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}

"""Rol A: reglas de validación de calidad de registros."""

import pandas as pd

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}

UNIDADES_PERMITIDAS = {
    "temperatura": {"°C", "C", "°c", "c"},
    "presion": {"hPa", "hpa"},
    "humedad": {"%"},
}


def validar_registro(registro: dict) -> tuple[bool, list[str]]:
    motivos = []

    campos_obligatorios = ["id", "tipo", "valor", "unidad"]
    for campo in campos_obligatorios:
        if (
            campo not in registro
            or registro[campo] is None
            or str(registro[campo]).strip() == ""
        ):
            motivos.append(f"Campo obligatorio ausente o vacío: '{campo}'")

    if motivos:
        return False, motivos

    tipo = registro["tipo"]
    unidad = registro["unidad"]
    valor_raw = registro["valor"]

    if tipo not in TIPOS_PERMITIDOS:
        motivos.append(
            f"Tipo no permitido '{tipo}'. Tipos válidos: {sorted(list(TIPOS_PERMITIDOS))}"
        )

    try:
        float(valor_raw)
    except (ValueError, TypeError):
        motivos.append(
            f"El valor '{valor_raw}' no tiene un formato numérico válido."
        )

    if tipo in UNIDADES_PERMITIDAS:
        if unidad not in UNIDADES_PERMITIDAS[tipo]:
            motivos.append(
                f"Unidad '{unidad}' no válida para el tipo '{tipo}'. Permitidas: {sorted(list(UNIDADES_PERMITIDAS[tipo]))}"
            )

    es_valido = len(motivos) == 0
    return es_valido, motivos


# 1. Cargar archivo limpio previamente procesado
ruta_entrada = (
    r"C:\Repositorio\Proyecto-integrador\data\processed\temperatura_limpio.csv"
)
df = pd.read_csv(ruta_entrada)

# 2. Iterar registros y validar
validos = []
rechazados = []

for registro in df.to_dict(orient="records"):
    es_valido, motivos = validar_registro(registro)

    if es_valido:
        validos.append(registro)
    else:
        # Añadimos los errores al registro para trazabilidad
        registro_rechazado = registro.copy()
        registro_rechazado["motivos_rechazo"] = " | ".join(motivos)
        rechazados.append(registro_rechazado)

# 3. Guardar resultados
df_validos = pd.DataFrame(validos)
df_rechazados = pd.DataFrame(rechazados)

ruta_validos = r"C:\Repositorio\Proyecto-integrador\data\processed\temperatura_validado.csv"
ruta_rechazados = r"C:\Repositorio\Proyecto-integrador\data\processed\temperatura_rechazados.csv"

df_validos.to_csv(ruta_validos, index=False)
df_rechazados.to_csv(ruta_rechazados, index=False)

print(
    f"Proceso finalizado.\n"
    f" - Registros válidos ({len(validos)}): {ruta_validos}\n"
    f" - Registros rechazados ({len(rechazados)}): {ruta_rechazados}"
)