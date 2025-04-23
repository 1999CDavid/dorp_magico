def calcular_costo_total(matriz_costos_variables, costos_fijos, instalaciones_abiertas):
    """Calcula el costo total (fijos + variables)"""
    if not instalaciones_abiertas:
        return float('inf')
    
    costo_fijo = sum(costos_fijos[i] for i in instalaciones_abiertas)
    costo_variable = 0.0
    
    for cliente in range(len(matriz_costos_variables[0])):
        # Asegurarse de que hay al menos una instalación abierta
        if not instalaciones_abiertas:
            return float('inf')
        costo_min = min(matriz_costos_variables[inst][cliente] 
                       for inst in instalaciones_abiertas)
        costo_variable += costo_min
    
    return float(costo_fijo + costo_variable)

def algoritmo_drop(matriz_costos_variables, costos_fijos):
    """Versión corregida del algoritmo DROP"""
    n_instalaciones = len(costos_fijos)
    instalaciones_abiertas = list(range(n_instalaciones))
    
    # Calcular costo inicial
    mejor_costo = calcular_costo_total(matriz_costos_variables, costos_fijos, instalaciones_abiertas)
    if mejor_costo == float('inf'):
        return [], mejor_costo
    
    mejoras = True
    while mejoras and len(instalaciones_abiertas) > 1:  # Nunca dejar sin instalaciones
        mejoras = False
        mejor_cierre = None
        mejor_costo_iteracion = float('inf')
        
        # Probar cerrar cada instalación
        for i in range(len(instalaciones_abiertas)):
            temp_abiertas = [x for x in instalaciones_abiertas if x != instalaciones_abiertas[i]]
            nuevo_costo = calcular_costo_total(matriz_costos_variables, costos_fijos, temp_abiertas)
            
            if nuevo_costo < mejor_costo_iteracion:
                mejor_costo_iteracion = nuevo_costo
                mejor_cierre = i
        
        # Si encontramos mejora, aplicarla
        if mejor_costo_iteracion < mejor_costo:
            instalaciones_abiertas.pop(mejor_cierre)
            mejor_costo = mejor_costo_iteracion
            mejoras = True
    
    # Convertir a base 1 para mostrar al usuario
    return [x+1 for x in instalaciones_abiertas], mejor_costo