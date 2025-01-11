from pprint import pprint

# Definiendo las constantes
costo_agencia_fijo = 900000
margen_producto = 0.30
recargo_agencia = 0.05

# Inversiones
inversiones = [1.5e6, 2.5e6, 3.5e6]

# Funciones de cálculo
def calcular_costo_total(inversion):
    return inversion + (inversion * recargo_agencia) + costo_agencia_fijo

def calcular_ventas_necesarias(costo_total):
    return costo_total / margen_producto

def calcular_roas(ventas, inversion):
    return ventas / inversion

def calcular_porcentaje_inversion(inversion, ventas_necesarias):
    return (inversion / ventas_necesarias) * 100

# Realizar los cálculos para cada inversión
resultados = []
for inversion in inversiones:
    costo_total = calcular_costo_total(inversion)
    ventas_necesarias = calcular_ventas_necesarias(costo_total)
    roas = calcular_roas(ventas_necesarias, inversion)
    porcentaje_inversion = calcular_porcentaje_inversion(inversion, ventas_necesarias)
    resultados.append({
        "Inversion": inversion,
        # "Costo Total": costo_total,
        # "Ventas Necesarias": ventas_necesarias,
        "ROAS": roas,
        "Porcentaje de Inversion": porcentaje_inversion
    })

pprint(resultados)
