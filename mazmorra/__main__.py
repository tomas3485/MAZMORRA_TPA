# punto de entrada: python -m mazmorra  (interfaz grafica)  o  python -m mazmorra --consola.
import argparse
import logging
import sys

from . import __version__
from .juego import RUTA_DATOS, Juego, configurar_logging
from .modelo import ErrorMazmorra

logger = logging.getLogger(__name__)


def demo_consola(juego: Juego, nombre: str, exportar: str | None) -> None:
    # Demo sin interfaz: carga la partida (o crea una nueva), juega sola la primera
    # mazmorra, guarda el progreso y, si se pide, exporta la campaña.
    juego.suscribir(print)
    if not juego.cargar():
        juego.nueva_partida(nombre)
    if not juego.campana.mazmorras:
        juego.generar_mazmorra()

    def equipar_si_mejora(objeto) -> bool:
        # Decide si el personaje coge un objeto: solo si es mejor que el que lleva.
        actual = juego.personaje.objeto_equipado
        return actual is None or objeto.bonus > actual.bonus

    for _ in range(40):  # tope por si pierde muchas veces seguidas
        if juego.avanzar(0, equipar_si_mejora) == "completada":
            break
    juego.guardar()
    print(f"Guardado en {juego.ruta}")
    if exportar:
        ruta = f"campana.{exportar}"
        juego.exportar(exportar, ruta)
        print(f"Exportado en {ruta}")


def main(argv: list[str] | None = None) -> int:
    # Lee los argumentos de la línea de comandos y arranca el juego: demo en consola
    # (--consola) o interfaz gráfica. Devuelve 0 si todo va bien y 1 si hay un error del juego.
    parser = argparse.ArgumentParser(prog="mazmorra", description="Mazmorras olvidadas")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--consola", action="store_true", help="demo en consola, sin interfaz grafica")
    parser.add_argument("--archivo", default=RUTA_DATOS, help="json de la partida")
    parser.add_argument("--nombre", default="Heroe", help="nombre del personaje en la demo de consola")
    parser.add_argument("--semilla", type=int, default=None, help="semilla del generador")
    parser.add_argument("--exportar", choices=["json", "md"], help="formato de exportacion (demo)")
    args = parser.parse_args(argv)

    configurar_logging()
    juego = Juego(args.archivo, args.semilla)
    try:
        if args.consola:
            demo_consola(juego, args.nombre, args.exportar)
        else:
            from .interfaz import lanzar  # tkinter solo se importa si hace falta

            lanzar(juego)
    except ErrorMazmorra as error:
        logger.error("Error: %s", error)
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())