import pytest
from modelo import Campaña, Mazmorra, Sala, Enemigo, Objeto, Personaje

# 1. pruebas basicas para ver que las clases se crean bien y no fallan

#ASSERT: comprueba que una condición es verdadera; si no lo es, el test falla y pytest te dice exactamente cuál
# es la base de como funciona cualquier test en pytest.

def test_crear_enemigo_basico():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    assert goblin.nombre_e == "Goblin"
    assert goblin.vida == 10


def test_mazmorra_contiene_sala_con_enemigo():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    sala = Sala((0, 0), "entrada", objetos=[], enemigos=[goblin])
    mazmorra = Mazmorra("Cripta", tesoro=100.0, salas=[sala])

    assert mazmorra.salas[0].enemigos[0] is goblin
    assert mazmorra.esta_despejada() is False


# 2. comparamos identidad (is) e igualdad (==), que parecen lo mismo pero no lo son


def test_identidad_vs_igualdad_con_alias():
    goblin_a = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    goblin_b = goblin_a  

    assert goblin_a is goblin_b          
    assert id(goblin_a) == id(goblin_b)  
    assert goblin_a == goblin_b         


def test_identidad_vs_igualdad_con_copias_distintas():
    goblin_1 = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    goblin_2 = Enemigo("Goblin", vida=10, ataque=3, defensa=1)  

    assert goblin_1 is not goblin_2          
    assert id(goblin_1) != id(goblin_2)      
    assert goblin_1 == goblin_2              


def test_eq_devuelve_false_si_difieren_los_datos():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    orco = Enemigo("Orco", vida=20, ataque=5, defensa=3)

    assert goblin != orco


# 3. bug del argumento por defecto mutable, provocado aqui aparte y luego corregido (nuestra Sala real no lo tiene porque objetos y enemigos son obligatorios)

def crear_lista_con_bug(elemento, lista=[]):   # el bug esta aqui, la lista solo se crea una vez
    lista.append(elemento)
    return lista


def crear_lista_corregida(elemento, lista=None):  
    if lista is None:
        lista = []
    lista.append(elemento)
    return lista


def test_bug_argumento_por_defecto_mutable():
    resultado_1 = crear_lista_con_bug("espada")
    resultado_2 = crear_lista_con_bug("poción")

    # la segunda llamada arrastra lo de la primera porque comparten la misma lista
    assert resultado_1 is resultado_2
    assert resultado_1 == ["espada", "poción"]


def test_correccion_argumento_por_defecto_mutable():
    resultado_1 = crear_lista_corregida("espada")
    resultado_2 = crear_lista_corregida("poción")

    # ahora cada llamada tiene su propia lista y no se mezclan
    assert resultado_1 is not resultado_2
    assert resultado_1 == ["espada"]
    assert resultado_2 == ["poción"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])