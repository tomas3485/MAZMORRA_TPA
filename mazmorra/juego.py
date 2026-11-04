import copy
import logging
import os

from .modelo import (
    Campaña,
    Combate,
    DatoInvalidoError,
    ErrorMazmorra,
    GeneradorMazmorras,
    Personaje,
)
from .persistencia import cargar_partida, exportar_campana, guardar_partida

logger = logging.getLogger(__name__)

# configuracion: se puede cambiar con variables de entorno sin tocar el codigo
# NOTA DE SEGURIDAD: no hay contraseñas ni claves. El json se trata como dato no fiable:
# se valida al cargarlo y nunca se ejecuta (nada de pickle, eval ni exec)..
RUTA_DATOS = os.environ.get("MAZMORRA_DATOS", "partida.json")
NIVEL_LOG = os.environ.get("MAZMORRA_LOG", "INFO").upper()
FICHERO_LOG = os.environ.get("MAZMORRA_LOGFILE", "mazmorra.log")

MAZMORRAS_INICIALES = 3  # las que hay al empezar una partida nueva
MAX_PENDIENTES = 8  # para que no se acumulen mazmorras sin fin


def configurar_logging() -> None:
    # solo se llama desde el punto de entrada, no al importar, para no molestar a los tests
    nivel = getattr(logging, NIVEL_LOG, logging.INFO)
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(FICHERO_LOG, encoding="utf-8")],
    )


# PATRON FACADE: la interfaz y la consola solo hablan con Juego, que coordina
# el generador, el combate, la persistencia y la exportacion
class Juego:
    def __init__(self, ruta: str = RUTA_DATOS, semilla: int | None = None):
        self.ruta = ruta
        self.generador = GeneradorMazmorras(semilla)
        self.observadores = []  # funciones que reciben cada mensaje de la partida (la interfaz, print...)
        self.personaje: Personaje | None = None
        self.campana: Campaña | None = None
        self.completadas = 0

    @property
    def nivel(self) -> int:
        return self.completadas + 1

    def suscribir(self, observador) -> None:
        self.observadores.append(observador)

    def _emitir(self, texto: str) -> None:
        logger.info(texto)
        for observador in self.observadores:
            observador(texto)

    # partida
    def nueva_partida(self, nombre: str, iniciales: int = MAZMORRAS_INICIALES) -> None:
        self.personaje = Personaje(nombre, 50, 6, 2, [])
        self.campana = Campaña("Las mazmorras olvidadas", "Limpia todas las mazmorras que puedas", [])
        self.completadas = 0
        for _ in range(iniciales):
            self.generar_mazmorra()
        self._emitir(f"{nombre} empieza su aventura")

    def generar_mazmorra(self):
        if len(self.campana.mazmorras) >= MAX_PENDIENTES:
            raise ErrorMazmorra(f"Ya hay {MAX_PENDIENTES} mazmorras pendientes, completa alguna primero")
        usados = {m.nombre_m for m in self.campana.mazmorras}
        mazmorra = self.generador.generar_aleatoria(usados)
        self.campana.mazmorras.append(mazmorra)
        self._emitir(f"Aparece {mazmorra.nombre_m} ({len(mazmorra.salas)} salas)")
        return mazmorra

    def avanzar(self, indice: int, decidir_equipar) -> str:
        """Entra en la siguiente sala de una mazmorra. decidir_equipar(objeto) -> bool lo pone la interfaz.

        Devuelve "victoria", "objeto", "vacia", "derrota" o "completada".
        """
        mazmorras = self.campana.mazmorras
        if isinstance(indice, bool) or not isinstance(indice, int) or not 0 <= indice < len(mazmorras):
            raise DatoInvalidoError(f"No existe la mazmorra {indice!r}")
        mazmorra = mazmorras[indice]
        sala = mazmorra.sala_actual()  # siempre la que toca, no se puede saltar ninguna
        if sala is None:
            raise DatoInvalidoError("Esa mazmorra ya está completada")

        if sala.enemigos:
            if not self._combatir(mazmorra, sala):
                return "derrota"
            estado = "victoria"
        elif sala.objetos:
            self._recoger(sala, decidir_equipar)
            estado = "objeto"
        else:
            estado = "vacia"

        mazmorra.avanzar()
        if mazmorra.completada():
            self._completar(mazmorra)
            return "completada"
        return estado

    def _combatir(self, mazmorra, sala) -> bool:
        for original in sala.enemigos:
            # se lucha contra una copia para que el enemigo de la mazmorra quede intacto si perdemos
            enemigo = copy.copy(original)
            self._emitir(f"{self.personaje.nombre} se enfrenta a {enemigo.nombre}")
            if not Combate(self.personaje, enemigo, [self._emitir]).ejecutar():
                self._emitir(f"Has caído ante {enemigo.nombre}. {mazmorra.nombre_m} vuelve a empezar")
                mazmorra.reiniciar()
                self.personaje.curar()
                return False
            self._emitir(f"Has derrotado a {enemigo.nombre}")
        return True

    def _recoger(self, sala, decidir_equipar) -> None:
        for objeto in sala.objetos:
            if decidir_equipar(objeto):
                self.personaje.equipar(objeto)
                self._emitir(f"Te equipas con {objeto.nombre_o} (+{objeto.bonus} ataque)")
            else:
                self._emitir(f"Dejas {objeto.nombre_o} donde estaba")

    def _completar(self, mazmorra) -> None:
        # la mazmorra desaparece de la lista, el personaje cobra el tesoro y sube de nivel
        self.campana.mazmorras.remove(mazmorra)
        self.completadas += 1
        self.personaje.oro += mazmorra.tesoro
        self.personaje.vida_max += 5
        self.personaje.ataque += 1
        self.personaje.curar()
        self._emitir(f"¡{mazmorra.nombre_m} completada! +{mazmorra.tesoro} de oro. Subes al nivel {self.nivel}")

    # guardar, cargar y exportar
    def guardar(self) -> None:
        guardar_partida(self.ruta, self.personaje, self.campana, self.completadas)

    def cargar(self) -> bool:
        # True si habia partida guardada, False si el fichero no existe (se queda lo que hubiera)
        try:
            self.personaje, self.campana, self.completadas = cargar_partida(self.ruta)
        except FileNotFoundError:
            return False
        return True

    def exportar(self, formato: str, ruta: str) -> None:
        exportar_campana(self.campana, formato, ruta)
