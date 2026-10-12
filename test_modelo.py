import pytest
from modelo import (Campaña, Mazmorra, Sala, Enemigo, Objeto, Personaje,
                    Entidad, Combate, GeneradorMazmorras)

# 1. pruebas basicas para ver que las clases se crean bien y no fallan

#ASSERT: comprueba que una condición es verdadera; si no lo es, el test falla y pytest te dice exactamente cuál
# es la base de como funciona cualquier test en pytest.

def test_crear_enemigo_basico():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    assert goblin.nombre == "Goblin"
    assert goblin.vida == 10


def test_mazmorra_contiene_sala_con_enemigo():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    sala = Sala(0, "entrada", objetos=[], enemigos=[goblin])  # la posicion ahora es un entero
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


# 4. validaciones y herencia
# pytest.raises comprueba que el codigo lanza la excepcion esperada; si no la lanza, el test falla

def test_vida_negativa_lanza_error():
    with pytest.raises(ValueError):
        Enemigo("Goblin", vida=-1, ataque=3, defensa=1)


def test_personaje_y_enemigo_heredan_de_entidad():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    heroe = Personaje("Aria", vida=30, ataque=5, defensa=2, inventario=[])

    assert isinstance(goblin, Entidad)
    assert isinstance(heroe, Entidad)


# 5. daño y ataque

def test_recibir_dano_no_baja_de_cero():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)

    goblin.recibir_dano(100)  # mas daño que vida: se queda en 0, no en negativo
    assert goblin.vida == 0
    assert goblin.esta_vivo() is False


def test_atacar_usa_la_defensa_del_objetivo():
    heroe = Personaje("Aria", vida=30, ataque=5, defensa=2, inventario=[])
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)

    dano = heroe.atacar(goblin)  # 5 - 1 = 4
    assert dano == 4
    assert goblin.vida == 6


# 6. combate: no hay aleatoriedad asi que el resultado se puede calcular a mano

def test_combate_gana_el_personaje_fuerte():
    heroe = Personaje("Aria", vida=50, ataque=8, defensa=3, inventario=[])
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)

    assert Combate(heroe, goblin).ejecutar() is True
    assert goblin.esta_vivo() is False


def test_combate_pierde_el_personaje_debil():
    heroe = Personaje("Debil", vida=5, ataque=1, defensa=0, inventario=[])
    orco = Enemigo("Orco", vida=20, ataque=5, defensa=3)

    assert Combate(heroe, orco).ejecutar() is False
    assert heroe.esta_vivo() is False


# 7. generador: la clave es que con la misma semilla salga lo mismo

def test_misma_semilla_genera_la_misma_mazmorra():
    m1 = GeneradorMazmorras(semilla=7).generar_mazmorra("Cripta", num_salas=4)
    m2 = GeneradorMazmorras(semilla=7).generar_mazmorra("Cripta", num_salas=4)

    assert repr(m1) == repr(m2)


def test_estructura_de_la_mazmorra_generada():
    mazmorra = GeneradorMazmorras(semilla=1).generar_mazmorra("Cripta", num_salas=4)

    assert len(mazmorra.salas) == 4
    assert mazmorra.salas[0].tipo == "entrada"
    assert mazmorra.salas[0].enemigos == []   # la entrada es segura


def test_generador_sin_salas_lanza_error():
    with pytest.raises(ValueError):
        GeneradorMazmorras(semilla=1).generar_mazmorra("Cripta", num_salas=0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])