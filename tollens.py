def modus_tollens(Q, P_implica_Q):
    if not Q and P_implica_Q:
        return False  # Se niega P
    return True  # No se puede concluir nada

# Ejemplo
hay_humo = False
fuego_implica_humo = True

if not modus_tollens(hay_humo, fuego_implica_humo):
    print("Conclusión: No hay fuego.")
else:
    print("No se puede concluir nada.")
