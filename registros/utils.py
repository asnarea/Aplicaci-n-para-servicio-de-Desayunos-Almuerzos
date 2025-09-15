from datetime import time

def clasificar_consumo(dt_local):
    hora = dt_local.time()
    if time(6, 0) <= hora <= time(9, 0):
        return 'DESAYUNO'

    if time(12, 00) <= hora <= time(14, 30):
        return 'ALMUERZO'
    return None