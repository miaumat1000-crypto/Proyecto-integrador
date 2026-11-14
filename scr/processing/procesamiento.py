"""Orquestación del procesamiento.

Semana 10-12: completar integración con validación y excepciones.
La clasificación permanece centralizada en clasificacion.py.
"""
from src.processing.clasificacion import clasificar_valor
from src.exceptions.errores import (
    DataLabError,
    ErrorValidacion,
    ErrorFormatoFuente,
    ErrorLecturaFuente,
    crear_reporte_error
)

def procesar_registros(registros):
    """Procesa un lote de registros de manera robusta, aislando errores individuales."""
    resultados_validos = []
    errores_detectados = []

    for reg in registros:
        try:
            # Extraer campos clave de forma segura
            identificador = str(reg.get("id", "DESCONOCIDO"))
            tipo_dato = str(reg.get("tipo", "general"))
            valor_bruto = reg.get("valor")

            # Validar si el valor está vacío, nulo o representa un error típico
            if valor_bruto is None or str(valor_bruto).strip() == "" or str(valor_bruto).upper() in ["N/D", "ERROR", "SIN_DATO", "DESCONOCIDO", "NA", "?", "PENDIENTE", "SIN LECTURA"]:
                raise ErrorValidacion(f"Valor no válido o ausente: {valor_bruto}")

            # Intentar convertir el valor a numérico
            try:
                valor_numerico = float(valor_bruto)
            except (ValueError, TypeError):
                raise ErrorValidacion(f"No se pudo convertir el valor a numérico: {valor_bruto}")

            # Clasificar el valor usando la función importada de clasificacion.py
            clasificacion = clasificar_valor(valor_numerico, tipo_dato)

            # Construir objeto válido común
            registro_procesado = {
                "id": identificador,
                "tipo": tipo_dato,
                "valor": valor_numerico,
                "unidad": str(reg.get("unidad", "")),
                "clasificacion": clasificacion
            }
            resultados_validos.append(registro_procesado)

        except DataLabError as e:
            # Aislar el error específico del registro y registrarlo sin detener el lote
            reporte = crear_reporte_error(
                origen="procesamiento_lote",
                identificador=reg.get("id", "N/A"),
                mensaje=str(e),
                categoria="VALIDACION"
            )
            errores_detectados.append(reporte)
        except Exception as e:
            # Capturar cualquier otro error inesperado del sistema
            reporte = crear_reporte_error(
                origen="procesamiento_lote",
                identificador=reg.get("id", "N/A"),
                mensaje=f"Error inesperado: {str(e)}",
                categoria="SISTEMA"
            )
            errores_detectados.append(reporte)

    return {
        "validos": resultados_validos,
        "errores": errores_detectados
    }
