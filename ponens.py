def modus_ponens(P, P_implica_Q):
    if P and P_implica_Q:
        return True
    return False

# Ejemplo
hay_nubes = True
nubes_implican_lluvia = True

if modus_ponens(hay_nubes, nubes_implican_lluvia):
    print("Conclusión: Va a llover.")
else:
    print("No se puede concluir nada.")
