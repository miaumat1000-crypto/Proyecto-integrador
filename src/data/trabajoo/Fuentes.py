from src.data.sensores import obtener_registros

def cargar_desde_memoria():
    """Fuente de datos funcional desde la primera entrega."""
    return obtener_registros()

def preparar_registros_prueba():
    """Rol C: escenarios adicionales de entrada para pruebas de semana 10."""
    # TODO C-S10-01: construir registros con espacios, mayúsculas y formatos diversos.
    # TODO C-S10-02: construir casos incompletos y tipos no reconocidos.
    # TODO C-S10-03: no alterar los 12 registros base.
    registros_adicionales = [
        {"id": " TST-01 ", "tipo": "TEMPERATURA", "valor": " 25.5 ", "unidad": " °C "},
        {"id": "TST-02", "tipo": "Humedad", "valor": "80", "unidad": "%"},
        {"id": "TST-03", "tipo": "desconocido", "valor": "abc", "unidad": "n/a"}, # Tipo no reconocido / datos incompletos
        {"id": "", "tipo": "PRESION", "valor": "", "unidad": "hPa"}              # Caso incompleto
    ]
    return registros_adicionales