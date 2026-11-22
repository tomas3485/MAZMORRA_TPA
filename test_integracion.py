from mazmorra.juego import Juego


def test_partida_completa_de_principio_a_fin(tmp_path):
    """Integración: genera, juega, guarda, recarga y exporta, usando juego+persistencia+modelo juntos."""
    ruta = str(tmp_path / "partida.json")
    juego = Juego(ruta=ruta, semilla=7)
    juego.nuevapartida("Aria", iniciales=1)

    # jugar la primera mazmorra hasta completarla o perder, sin bucles infinitos
    for _ in range(50):
        estado = juego.avanzar(0, lambda objeto: True)
        if estado == "completada":
            break
    else:
        raise AssertionError("la mazmorra no se completó en 50 intentos")

    juego.guardar()

    recargado = Juego(ruta=ruta)
    assert recargado.cargar() is True
    assert recargado.personaje.nombre == "Aria"
    assert recargado.completadas == juego.completadas

    destino = tmp_path / "campana.md"
    recargado.exportar("md", str(destino))
    assert destino.exists()