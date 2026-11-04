import logging

import pytest

import mazmorra.juego as modulo_juego
from mazmorra.juego import MAX_PENDIENTES, Juego
from mazmorra.modelo import (
    Campaña,
    DatoInvalidoError,
    ErrorMazmorra,
    ErrorPersistencia,
    Goblin,
    Mazmorra,
    Objeto,
    Orco,
    Personaje,
    Sala,
)


def juego_con(salas, personaje=None, tesoro=100.0):
    """Juego con una única mazmorra hecha a mano, para que todo sea predecible."""
    juego = Juego(ruta="no_se_usa.json", semilla=1)
    juego.personaje = personaje or Personaje("Aria", 50, 8, 3, [])
    juego.campana = Campaña("Camp", "Desc", [Mazmorra("Cripta", tesoro, salas)])
    return juego


ESPADA = Objeto("Espada", "arma", "Una espada", 3)


# ---------------------------------------------------------------------
# Partida nueva y generación
# ---------------------------------------------------------------------


def test_nueva_partida():
    juego = Juego(ruta="no_se_usa.json", semilla=1)

    juego.nueva_partida("Aria", iniciales=2)

    assert juego.personaje.nombre == "Aria"
    assert len(juego.campana.mazmorras) == 2
    assert juego.completadas == 0
    assert juego.nivel == 1


def test_los_observadores_reciben_los_mensajes():
    mensajes = []
    juego = Juego(ruta="no_se_usa.json", semilla=1)
    juego.suscribir(mensajes.append)

    juego.nueva_partida("Aria", iniciales=1)

    assert "Aria empieza su aventura" in mensajes


def test_no_se_pueden_acumular_mas_mazmorras_del_maximo():
    juego = Juego(ruta="no_se_usa.json", semilla=1)
    juego.nueva_partida("Aria", iniciales=MAX_PENDIENTES)

    with pytest.raises(ErrorMazmorra):
        juego.generar_mazmorra()


def test_las_mazmorras_generadas_no_repiten_nombre():
    juego = Juego(ruta="no_se_usa.json", semilla=1)
    juego.nueva_partida("Aria", iniciales=MAX_PENDIENTES)

    nombres = [m.nombre_m for m in juego.campana.mazmorras]

    assert len(nombres) == len(set(nombres))


# ---------------------------------------------------------------------
# Avanzar por las salas
# ---------------------------------------------------------------------


@pytest.mark.parametrize("indice", [-1, 5, "0", True])
def test_avanzar_con_indice_invalido(indice):
    juego = juego_con([Sala(0, "entrada", [], []), Sala(1, "normal", [], [])])

    with pytest.raises(DatoInvalidoError):
        juego.avanzar(indice, lambda o: True)


def test_avanzar_en_una_mazmorra_ya_completada_lanza_error():
    juego = juego_con([Sala(0, "entrada", [], []), Sala(1, "normal", [], [])])
    juego.campana.mazmorras[0].avanzar()  # la completa a mano

    with pytest.raises(DatoInvalidoError):
        juego.avanzar(0, lambda o: True)


def test_sala_vacia():
    juego = juego_con([Sala(0, "entrada", [], []), Sala(1, "normal", [], []), Sala(2, "normal", [], [])])

    assert juego.avanzar(0, lambda o: True) == "vacia"


def test_sala_con_enemigo_gana_el_personaje():
    salas = [Sala(0, "entrada", [], []), Sala(1, "enemigo", [], [Goblin("Goblin", 10, 3, 1)]), Sala(2, "normal", [], [])]
    juego = juego_con(salas)

    assert juego.avanzar(0, lambda o: True) == "victoria"
    assert juego.campana.mazmorras[0].progreso == 2


def test_sala_con_objeto_y_el_jugador_lo_equipa():
    salas = [Sala(0, "entrada", [], []), Sala(1, "objeto", [ESPADA], []), Sala(2, "normal", [], [])]
    juego = juego_con(salas)

    assert juego.avanzar(0, lambda o: True) == "objeto"
    assert juego.personaje.inventario == [ESPADA]


def test_sala_con_objeto_y_el_jugador_lo_deja():
    salas = [Sala(0, "entrada", [], []), Sala(1, "objeto", [ESPADA], []), Sala(2, "normal", [], [])]
    juego = juego_con(salas)

    assert juego.avanzar(0, lambda o: False) == "objeto"
    assert juego.personaje.inventario == []


def test_perder_un_combate_reinicia_la_mazmorra_y_cura_sin_tocar_al_enemigo():
    orco = Orco("Orco", 20, 5, 3)
    juego = juego_con([Sala(0, "entrada", [], []), Sala(1, "enemigo", [], [orco])], Personaje("Debil", 5, 1, 0, []))

    assert juego.avanzar(0, lambda o: True) == "derrota"

    assert juego.campana.mazmorras[0].progreso == 1
    assert juego.personaje.vida == juego.personaje.vida_max
    assert orco.vida == 20  # se luchó contra una copia


def test_completar_una_mazmorra_da_oro_nivel_y_la_quita_de_la_lista():
    juego = juego_con([Sala(0, "entrada", [], []), Sala(1, "objeto", [ESPADA], [])], tesoro=100.0)
    oro_antes = juego.personaje.oro

    assert juego.avanzar(0, lambda o: True) == "completada"

    assert juego.campana.mazmorras == []
    assert juego.completadas == 1
    assert juego.nivel == 2
    assert juego.personaje.oro == oro_antes + 100.0
    assert juego.personaje.vida_max == 55
    assert juego.personaje.ataque == 9


# ---------------------------------------------------------------------
# Guardar, cargar y exportar
# ---------------------------------------------------------------------


def test_guardar_y_cargar_la_partida(tmp_path):
    ruta = str(tmp_path / "partida.json")
    juego = Juego(ruta=ruta, semilla=1)
    juego.nueva_partida("Aria", iniciales=2)
    juego.guardar()

    otro = Juego(ruta=ruta)

    assert otro.cargar() is True
    assert otro.personaje.nombre == "Aria"
    assert len(otro.campana.mazmorras) == 2
    assert otro.completadas == 0


def test_cargar_sin_fichero_devuelve_false(tmp_path):
    assert Juego(ruta=str(tmp_path / "no_existe.json")).cargar() is False


def test_cargar_un_fichero_roto_lanza_error_propio(tmp_path):
    ruta = tmp_path / "partida.json"
    ruta.write_text("{no es json", encoding="utf-8")

    with pytest.raises(ErrorPersistencia):
        Juego(ruta=str(ruta)).cargar()


def test_exportar_a_markdown(tmp_path):
    juego = Juego(ruta="no_se_usa.json", semilla=1)
    juego.nueva_partida("Aria", iniciales=1)
    destino = tmp_path / "campana.md"

    juego.exportar("md", str(destino))

    assert destino.read_text(encoding="utf-8").startswith("# Las mazmorras olvidadas")


# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------


def test_configurar_logging_usa_el_nivel_y_el_fichero_de_la_configuracion(tmp_path, monkeypatch):
    llamadas = []
    monkeypatch.setattr(logging, "basicConfig", lambda **opciones: llamadas.append(opciones))
    monkeypatch.setattr(modulo_juego, "NIVEL_LOG", "DEBUG")
    monkeypatch.setattr(modulo_juego, "FICHERO_LOG", str(tmp_path / "prueba.log"))

    modulo_juego.configurar_logging()

    assert llamadas[0]["level"] == logging.DEBUG
    assert isinstance(llamadas[0]["handlers"][0], logging.FileHandler)
    llamadas[0]["handlers"][0].close()