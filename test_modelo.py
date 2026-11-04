import pytest
from mazmorra.modelo import (
    Campaña,
    Combate,
    DatoInvalidoError,
    Enemigo,
    Entidad,
    ErrorMazmorra,
    GeneradorMazmorras,
    Goblin,
    Mazmorra,
    NOMBRES_MAZMORRAS,
    Objeto,
    Orco,
    Personaje,
    Sala,
    crear_enemigo,
)

# ----------------------------------------------------------------------
# 1. Creación de objetos y relaciones entre clases
# ----------------------------------------------------------------------


def test_crear_enemigo_basico():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)

    assert goblin.nombre == "Goblin"
    assert goblin.vida == 10
    assert goblin.ataque == 3
    assert goblin.defensa == 1


def test_mazmorra_contiene_sala_con_enemigo():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    sala = Sala(0, "entrada", objetos=[], enemigos=[goblin])
    mazmorra = Mazmorra("Cripta", tesoro=100.0, salas=[sala])

    assert mazmorra.salas[0].enemigos[0] is goblin
    assert mazmorra.esta_despejada() is False


def test_crear_campana_con_mazmorra():
    mazmorra = Mazmorra("Cripta", 100.0, [])
    campana = Campaña("La aventura", "Una aventura de prueba", [mazmorra])

    assert campana.nombre_c == "La aventura"
    assert campana.mazmorras == [mazmorra]


def test_personaje_y_enemigo_heredan_de_entidad():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    heroe = Personaje("Aria", vida=30, ataque=5, defensa=2, inventario=[])

    assert isinstance(goblin, Entidad)
    assert isinstance(heroe, Entidad)


# ---------------------------------------------------------------------
# 2. Identidad e igualdad
# ---------------------------------------------------------------------


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


def test_igualdad_devuelve_false_si_difieren_los_datos():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)
    orco = Enemigo("Orco", vida=20, ataque=5, defensa=3)

    assert goblin != orco


# ---------------------------------------------------------------------
# 3. Argumentos mutables por defecto
# Se conserva este ejemplo didáctico, independiente de las clases reales.
# ---------------------------------------------------------------------


def crear_lista_con_bug(elemento, lista=[]):
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

    assert resultado_1 is resultado_2
    assert resultado_1 == ["espada", "poción"]


def test_correccion_argumento_por_defecto_mutable():
    resultado_1 = crear_lista_corregida("espada")
    resultado_2 = crear_lista_corregida("poción")

    assert resultado_1 is not resultado_2
    assert resultado_1 == ["espada"]
    assert resultado_2 == ["poción"]


# ---------------------------------------------------------------------
# 4. Validaciones de Entidad
# ---------------------------------------------------------------------


@pytest.mark.parametrize("vida", [-1, 1.5, "10", True])
def test_vida_invalida_lanza_error(vida):
    with pytest.raises(ValueError):
        Enemigo("Goblin", vida=vida, ataque=3, defensa=1)


@pytest.mark.parametrize("ataque", [-1, 2.5, "3", False])
def test_ataque_invalido_lanza_error(ataque):
    with pytest.raises(ValueError):
        Enemigo("Goblin", vida=10, ataque=ataque, defensa=1)


@pytest.mark.parametrize("defensa", [-1, 2.5, "1", True])
def test_defensa_invalida_lanza_error(defensa):
    with pytest.raises(ValueError):
        Enemigo("Goblin", vida=10, ataque=3, defensa=defensa)


@pytest.mark.parametrize("nombre", ["", "   ", None, 123])
def test_nombre_invalido_lanza_error(nombre):
    with pytest.raises(ValueError):
        Enemigo(nombre, vida=10, ataque=3, defensa=1)


def test_vida_cero_significa_que_la_entidad_no_esta_viva():
    goblin = Enemigo("Goblin", vida=0, ataque=3, defensa=1)

    assert goblin.esta_vivo() is False


# ---------------------------------------------------------------------
# 5. Validaciones de objetos, salas, mazmorras, campañas e inventario
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "nombre, tipo, descripcion",
    [
        ("", "arma", "Una espada"),
        ("Espada", "", "Una espada"),
        ("Espada", "arma", ""),
        (None, "arma", "Una espada"),
    ],
)
def test_objeto_con_datos_invalidos_lanza_error(nombre, tipo, descripcion):
    with pytest.raises(ValueError):
        Objeto(nombre, tipo, descripcion)


def test_crear_objeto_valido():
    objeto = Objeto("Espada", "arma", "Una espada de prueba")

    assert objeto.nombre_o == "Espada"
    assert objeto.tipo == "arma"
    assert objeto.descripcion_o == "Una espada de prueba"
    assert objeto.bonus == 0


@pytest.mark.parametrize("bonus", [-1, 1.5, "2", True])
def test_objeto_rechaza_bonus_invalido(bonus):
    with pytest.raises(ValueError):
        Objeto("Espada", "arma", "Una espada", bonus)


@pytest.mark.parametrize("posicion", [-1, 1.5, "0", True])
def test_posicion_de_sala_invalida_lanza_error(posicion):
    with pytest.raises(ValueError):
        Sala(posicion, "normal", [], [])


def test_sala_rechaza_elementos_que_no_son_objetos():
    with pytest.raises(ValueError):
        Sala(0, "entrada", ["espada"], [])


def test_sala_rechaza_elementos_que_no_son_enemigos():
    with pytest.raises(ValueError):
        Sala(0, "entrada", [], ["goblin"])


def test_mazmorra_rechaza_tesoro_negativo():
    with pytest.raises(ValueError):
        Mazmorra("Cripta", -1, [])


@pytest.mark.parametrize("tesoro", ["100", True, None])
def test_mazmorra_rechaza_tesoro_de_tipo_incorrecto(tesoro):
    with pytest.raises(ValueError):
        Mazmorra("Cripta", tesoro, [])


def test_mazmorra_rechaza_salas_de_tipo_incorrecto():
    with pytest.raises(ValueError):
        Mazmorra("Cripta", 100, ["sala"])


def test_campana_rechaza_mazmorras_de_tipo_incorrecto():
    with pytest.raises(ValueError):
        Campaña("Aventura", "Descripción", ["Cripta"])


def test_personaje_rechaza_inventario_de_tipo_incorrecto():
    with pytest.raises(ValueError):
        Personaje("Aria", 30, 5, 2, ["espada"])


# ---------------------------------------------------------------------
# 6. Daño y ataques
# ---------------------------------------------------------------------


def test_recibir_dano_no_baja_de_cero():
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)

    goblin.recibir_dano(100)

    assert goblin.vida == 0
    assert goblin.esta_vivo() is False


@pytest.mark.parametrize("cantidad", [-1, 1.5, "5", True])
def test_recibir_dano_rechaza_cantidades_invalidas(cantidad):
    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)

    with pytest.raises(ValueError):
        goblin.recibir_dano(cantidad)

    # La vida no debe cambiar cuando los datos son inválidos.
    assert goblin.vida == 10


def test_atacar_usa_la_defensa_del_objetivo():
    heroe = Personaje("Aria", 30, 5, 2, [])
    goblin = Enemigo("Goblin", 10, 3, 1)

    dano = heroe.atacar(goblin)

    assert dano == 4
    assert goblin.vida == 6


def test_el_ataque_hace_como_minimo_un_punto_de_dano():
    heroe = Personaje("Aria", 30, 1, 2, [])
    orco = Enemigo("Orco", 20, 5, 10)

    dano = heroe.atacar(orco)

    assert dano == 1
    assert orco.vida == 19


# ---------------------------------------------------------------------
# 7. Combate
# ---------------------------------------------------------------------


def test_combate_gana_el_personaje_fuerte():
    heroe = Personaje("Aria", 50, 8, 3, [])
    goblin = Enemigo("Goblin", 10, 3, 1)

    combate = Combate(heroe, goblin)

    assert combate.ejecutar() is True
    assert goblin.esta_vivo() is False
    assert len(combate.registro) > 0


def test_combate_pierde_el_personaje_debil():
    heroe = Personaje("Debil", 5, 1, 0, [])
    orco = Enemigo("Orco", 20, 5, 3)

    assert Combate(heroe, orco).ejecutar() is False
    assert heroe.esta_vivo() is False


def test_enemigo_no_contraataca_si_muere_en_el_primer_golpe():
    heroe = Personaje("Aria", 30, 20, 2, [])
    goblin = Enemigo("Goblin", 5, 3, 1)
    combate = Combate(heroe, goblin)

    resultado = combate.ejecutar()

    assert resultado is True
    assert heroe.vida == 30
    assert len(combate.registro) == 1


def test_combate_no_se_ejecuta_si_el_personaje_ya_esta_derrotado():
    heroe = Personaje("Aria", 0, 5, 2, [])
    goblin = Enemigo("Goblin", 10, 3, 1)
    combate = Combate(heroe, goblin)

    assert combate.ejecutar() is False
    assert goblin.vida == 10
    assert combate.registro == []


# ---------------------------------------------------------------------
# 8. Generador de mazmorras
# ---------------------------------------------------------------------


def test_misma_semilla_genera_la_misma_mazmorra():
    m1 = GeneradorMazmorras(semilla=7).generar_mazmorra("Cripta", 4)
    m2 = GeneradorMazmorras(semilla=7).generar_mazmorra("Cripta", 4)

    assert repr(m1) == repr(m2)


def test_estructura_de_la_mazmorra_generada():
    mazmorra = GeneradorMazmorras(semilla=1).generar_mazmorra("Cripta", 4)

    assert len(mazmorra.salas) == 4
    assert mazmorra.salas[0].tipo == "entrada"
    assert mazmorra.salas[0].enemigos == []


@pytest.mark.parametrize("num_salas", [0, 1, 2, -1, 1.5, "4", True])
def test_generador_rechaza_numero_de_salas_invalido(num_salas):
    with pytest.raises(ValueError):
        GeneradorMazmorras(semilla=1).generar_mazmorra("Cripta", num_salas=num_salas)


def test_generador_crea_enemigos_independientes():
    mazmorra = GeneradorMazmorras(semilla=3).generar_mazmorra("Cripta", 3)
    enemigos = mazmorra.enemigos_totales()

    # Si hay varios enemigos, modificar uno no debe modificar los demás.
    if len(enemigos) >= 2:
        vida_segundo = enemigos[1].vida
        enemigos[0].recibir_dano(1)
        assert enemigos[1].vida == vida_segundo


def test_mazmorra_sin_enemigos_esta_despejada():
    mazmorra = Mazmorra("Cripta", 100, [Sala(0, "entrada", [], [])])

    assert mazmorra.esta_despejada() is True


def test_polimorfismo_distintos_enemigos_distinto_dano():
    heroe = Personaje("Aria", 30, 5, 2, [])
    goblin = Goblin("Goblin", 10, 3, 1)
    orco = Orco("Orco", 20, 5, 3)

    dano_goblin = goblin.atacar(heroe)  # 3 - 2 = 1
    dano_orco = orco.atacar(heroe)  # (5+2) - 2 = 5

    assert dano_goblin != dano_orco


# ---------------------------------------------------------------------
# 9. Reglas nuevas de la mazmorra: salas lineales y mínimo de salas
# ---------------------------------------------------------------------


@pytest.mark.parametrize("semilla", range(30))
def test_toda_mazmorra_tiene_entrada_objeto_y_enemigo(semilla):
    mazmorra = GeneradorMazmorras(semilla).generar_mazmorra("Cripta", 3)
    tipos = [s.tipo for s in mazmorra.salas]

    assert tipos[0] == "entrada"
    assert sorted(tipos[1:]) == ["enemigo", "objeto"]  # en cualquier orden


@pytest.mark.parametrize("semilla", range(30))
def test_salas_de_enemigo_y_objeto_tienen_lo_que_toca(semilla):
    mazmorra = GeneradorMazmorras(semilla).generar_mazmorra("Cripta", 8)

    for sala in mazmorra.salas:
        if sala.tipo == "enemigo":
            assert len(sala.enemigos) == 1 and sala.objetos == []
        elif sala.tipo == "objeto":
            assert len(sala.objetos) == 1 and sala.enemigos == []
        else:
            assert sala.enemigos == [] and sala.objetos == []


def test_generar_aleatoria_respeta_limites_y_usa_los_nombres_de_la_lista():
    generador = GeneradorMazmorras(semilla=5)

    for _ in range(50):
        mazmorra = generador.generar_aleatoria()
        assert GeneradorMazmorras.MIN_SALAS <= len(mazmorra.salas) <= GeneradorMazmorras.MAX_SALAS
        assert mazmorra.nombre_m in NOMBRES_MAZMORRAS


def test_generar_aleatoria_no_repite_nombres_usados():
    usados = set(NOMBRES_MAZMORRAS[:-1])
    mazmorra = GeneradorMazmorras(semilla=5).generar_aleatoria(usados)

    assert mazmorra.nombre_m == NOMBRES_MAZMORRAS[-1]


def test_si_todos_los_nombres_estan_usados_sigue_generando():
    mazmorra = GeneradorMazmorras(semilla=5).generar_aleatoria(set(NOMBRES_MAZMORRAS))

    assert mazmorra.nombre_m in NOMBRES_MAZMORRAS


def test_hay_290_nombres_distintos():
    assert len(NOMBRES_MAZMORRAS) == len(set(NOMBRES_MAZMORRAS)) == 290


def test_el_progreso_empieza_despues_de_la_entrada():
    mazmorra = GeneradorMazmorras(semilla=1).generar_mazmorra("Cripta", 4)

    assert mazmorra.progreso == 1
    assert mazmorra.sala_actual() is mazmorra.salas[1]
    assert mazmorra.completada() is False


def test_avanzar_obliga_a_ir_sala_por_sala_hasta_completar():
    mazmorra = GeneradorMazmorras(semilla=1).generar_mazmorra("Cripta", 4)

    for esperada in mazmorra.salas[1:]:
        assert mazmorra.sala_actual() is esperada  # nunca se puede saltar una sala
        mazmorra.avanzar()

    assert mazmorra.completada() is True
    assert mazmorra.sala_actual() is None
    with pytest.raises(DatoInvalidoError):
        mazmorra.avanzar()


def test_reiniciar_devuelve_la_mazmorra_a_como_estaba():
    mazmorra = GeneradorMazmorras(semilla=1).generar_mazmorra("Cripta", 5)
    mazmorra.avanzar()
    mazmorra.avanzar()

    mazmorra.reiniciar()

    assert mazmorra.progreso == 1


@pytest.mark.parametrize("progreso", [-1, 5, 1.5, "1", True])
def test_mazmorra_rechaza_progreso_invalido(progreso):
    salas = [Sala(0, "entrada", [], []), Sala(1, "objeto", [], [])]
    with pytest.raises(ValueError):
        Mazmorra("Cripta", 10, salas, progreso)


def test_las_armas_buenas_son_mas_probables_en_las_salas_altas():
    generador = GeneradorMazmorras(semilla=11)
    n = 3000
    media_primera = sum(generador.elegir_arma(1, 8)[3] for _ in range(n)) / n
    media_ultima = sum(generador.elegir_arma(7, 8)[3] for _ in range(n)) / n

    assert media_ultima > media_primera + 1


def test_en_la_ultima_sala_la_mejor_arma_es_la_mas_probable():
    generador = GeneradorMazmorras(semilla=11)
    n = 3000
    bonus = [generador.elegir_arma(7, 8)[3] for _ in range(n)]
    mejor = max(a[3] for a in GeneradorMazmorras.ARMAS)

    assert bonus.count(mejor) == max(bonus.count(a[3]) for a in GeneradorMazmorras.ARMAS)


# ---------------------------------------------------------------------
# 10. Personaje: un solo objeto, arma equipada, oro y vida máxima
# ---------------------------------------------------------------------


def test_equipar_suma_el_bonus_al_ataque():
    heroe = Personaje("Aria", 30, 5, 2, [])
    goblin = Enemigo("Goblin", 10, 3, 1)
    heroe.equipar(Objeto("Espada", "arma", "Una espada", 3))

    assert heroe.ataque == 5  # el ataque base no cambia
    assert heroe.ataque_total == 8
    assert heroe.atacar(goblin) == 7  # 8 - 1


def test_solo_se_puede_llevar_un_objeto():
    heroe = Personaje("Aria", 30, 5, 2, [])
    espada = Objeto("Espada", "arma", "Una espada", 2)
    hacha = Objeto("Hacha", "arma", "Un hacha", 4)

    heroe.equipar(espada)
    heroe.equipar(hacha)  # sustituye a la espada

    assert heroe.inventario == [hacha]
    assert heroe.objeto_equipado is hacha


def test_personaje_rechaza_inventario_con_mas_de_un_objeto():
    objetos = [Objeto("A", "arma", "a"), Objeto("B", "arma", "b")]
    with pytest.raises(DatoInvalidoError):
        Personaje("Aria", 30, 5, 2, objetos)


def test_equipar_rechaza_algo_que_no_es_un_objeto():
    with pytest.raises(DatoInvalidoError):
        Personaje("Aria", 30, 5, 2, []).equipar("espada")


def test_sin_objeto_no_hay_arma_equipada():
    heroe = Personaje("Aria", 30, 5, 2, [])

    assert heroe.objeto_equipado is None
    assert heroe.ataque_total == 5


def test_curar_devuelve_la_vida_al_maximo():
    heroe = Personaje("Aria", 30, 5, 2, [], vida_max=50)
    assert heroe.vida_max == 50

    heroe.curar()

    assert heroe.vida == 50


def test_la_vida_maxima_por_defecto_es_la_vida_inicial():
    assert Personaje("Aria", 30, 5, 2, []).vida_max == 30


def test_la_vida_no_puede_superar_la_maxima():
    with pytest.raises(DatoInvalidoError):
        Personaje("Aria", 40, 5, 2, [], vida_max=30)


@pytest.mark.parametrize("vida_max", [0, -5, 2.5, "30", True])
def test_vida_maxima_invalida(vida_max):
    with pytest.raises(DatoInvalidoError):
        Personaje("Aria", 1, 5, 2, [], vida_max=vida_max)


@pytest.mark.parametrize("oro", [-1, "10", True, None])
def test_oro_invalido(oro):
    with pytest.raises(DatoInvalidoError):
        Personaje("Aria", 30, 5, 2, [], oro=oro)


# ---------------------------------------------------------------------
# 11. Factory, observer y excepciones propias
# ---------------------------------------------------------------------


@pytest.mark.parametrize("tipo, clase", [("Goblin", Goblin), ("Orco", Orco), ("Enemigo", Enemigo)])
def test_fabrica_crea_la_clase_correcta(tipo, clase):
    assert type(crear_enemigo(tipo, "X", 10, 3, 1)) is clase


def test_fabrica_rechaza_tipo_desconocido():
    with pytest.raises(DatoInvalidoError):
        crear_enemigo("Dragon", "X", 10, 3, 1)


def test_observador_recibe_cada_golpe_del_combate():
    eventos = []
    combate = Combate(Personaje("Aria", 50, 8, 3, []), Goblin("Goblin", 10, 3, 1), [eventos.append])

    combate.ejecutar()

    assert len(eventos) > 0
    assert eventos == combate.registro


def test_suscribir_despues_de_crear_el_combate():
    eventos = []
    combate = Combate(Personaje("Aria", 50, 8, 3, []), Goblin("Goblin", 10, 3, 1))
    combate.suscribir(eventos.append)

    combate.ejecutar()

    assert len(eventos) == len(combate.registro)


def test_dato_invalido_es_value_error_y_error_mazmorra():
    with pytest.raises(ValueError):
        Objeto("", "arma", "x")
    with pytest.raises(ErrorMazmorra):
        Objeto("", "arma", "x")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
