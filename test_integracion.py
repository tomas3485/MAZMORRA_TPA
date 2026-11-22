from mazmorra.juego import Juego


def test_partida_completa_de_principio_a_fin(tmp_path):
    """Integración: genera, juega, guarda, recarga y exporta, usando juego+persistencia+modelo juntos."""
    # Test de integración: crea una partida, juega una mazmorra y comprueba que
    # guardar, recargar y exportar funcionan bien juntos (usa una carpeta temporal).
    ruta = str(tmp_path / "partida.json")
    juego = Juego(ruta=ruta, semilla=7)
    juego.nueva_partida("Aria", iniciales=1)

    # jugar la primera mazmorra hasta completarla o perder, sin bucles infinitos
    for _ in range(50):
        estado = juego.avanzar(0, lambda objeto: True)
        if estado == "completada":
            break
    else:
        raise AssertionError("la mazmorra no se completó en 50 intentos")

    juego.guardar()

    # Se recarga la partida en una instancia nueva y se verifica que los datos se conservaron.
    recargado = Juego(ruta=ruta)
    assert recargado.cargar() is True
    assert recargado.personaje.nombre == "Aria"
    assert recargado.completadas == juego.completadas

    destino = tmp_path / "campana.md"
    recargado.exportar("md", str(destino))
    assert destino.exists()