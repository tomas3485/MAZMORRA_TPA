from __future__ import annotations  # sin esto Campaña da NameError porque usa Mazmorra antes de que este definida
import random
from pathlib import Path

# excepciones propias. DatoInvalidoError tambien es ValueError, asi los tests con pytest.raises(ValueError) siguen valiendo..
class ErrorMazmorra(Exception):
    pass


class DatoInvalidoError(ErrorMazmorra, ValueError):
    pass


class ErrorPersistencia(ErrorMazmorra):
    pass


class ErrorExportacion(ErrorMazmorra):
    pass


class Campaña:
    def __init__(self, nombre_c: str, descripcion: str, mazmorras: list[Mazmorra]):
        if not isinstance(nombre_c, str) or not nombre_c.strip():
            raise DatoInvalidoError("El nombre de la campaña no puede estar vacío")
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise DatoInvalidoError("La descripción no puede estar vacía")
        if not isinstance(mazmorras, list) or not all(isinstance(m, Mazmorra) for m in mazmorras):
            raise DatoInvalidoError("Las mazmorras deben ser una lista de objetos Mazmorra")

        self.nombre_c = nombre_c
        self.descripcion = descripcion
        self.mazmorras = mazmorras  # aqui solo estan las pendientes, las completadas se quitan

    def __repr__(self) -> str:
        return f"Campaña({self.nombre_c!r}, {self.descripcion!r}, {self.mazmorras})"


class Mazmorra:
    def __init__(self, nombre_m: str, tesoro: float, salas: list[Sala], progreso: int | None = None):
        if not isinstance(nombre_m, str) or not nombre_m.strip():
            raise DatoInvalidoError("El nombre de la mazmorra no puede estar vacío")
        if not isinstance(salas, list) or not all(isinstance(s, Sala) for s in salas):
            raise DatoInvalidoError("Las salas deben ser una lista de objetos Sala")
        # progreso = indice de la siguiente sala que hay que superar. La sala 0 (entrada) ya cuenta como superada
        if progreso is None:
            progreso = min(1, len(salas))
        if isinstance(progreso, bool) or not isinstance(progreso, int) or not 0 <= progreso <= len(salas):
            raise DatoInvalidoError("El progreso debe estar entre 0 y el número de salas")

        self.nombre_m = nombre_m
        self.tesoro = tesoro
        self.salas = salas
        self.progreso = progreso

    @property
    def tesoro(self):
        return self._tesoro

    @tesoro.setter
    def tesoro(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError("El tesoro debe ser un número")
        if valor < 0:
            raise DatoInvalidoError("El tesoro no puede ser negativo")
        self._tesoro = valor

    def enemigos_totales(self) -> list["Enemigo"]:
        return [e for sala in self.salas for e in sala.enemigos]

    def esta_despejada(self) -> bool:
        return not self.enemigos_totales()

    def completada(self) -> bool:
        return self.progreso >= len(self.salas)

    def sala_actual(self) -> Sala | None:
        # las salas son lineales: solo se puede entrar en la que toca, nunca saltarse ninguna
        return None if self.completada() else self.salas[self.progreso]

    def avanzar(self) -> None:
        if self.completada():
            raise DatoInvalidoError("La mazmorra ya está completada")
        self.progreso += 1

    def reiniciar(self) -> None:
        # si el personaje pierde, la mazmorra vuelve a como estaba al principio
        self.progreso = min(1, len(self.salas))

    def __repr__(self) -> str:
        return f"Mazmorra({self.nombre_m!r}, {self.tesoro}, {self.salas})"


class Sala:
    # la posicion es un entero (orden de la sala dentro de la mazmorra)
    # tipo: "entrada", "objeto" o "enemigo"
    def __init__(self, posicion: int, tipo: str, objetos: list[Objeto], enemigos: list[Enemigo]):
        if isinstance(posicion, bool) or not isinstance(posicion, int) or posicion < 0:
            raise DatoInvalidoError("La posición debe ser un entero no negativo")
        if not isinstance(tipo, str) or not tipo.strip():
            raise DatoInvalidoError("El tipo de sala no puede estar vacío")
        if not isinstance(objetos, list) or not all(isinstance(o, Objeto) for o in objetos):
            raise DatoInvalidoError("Los objetos deben estar en una lista de objetos Objeto")
        if not isinstance(enemigos, list) or not all(isinstance(e, Enemigo) for e in enemigos):
            raise DatoInvalidoError("Los enemigos deben estar en una lista de objetos Enemigo")

        self.posicion = posicion
        self.tipo = tipo
        self.objetos = objetos
        self.enemigos = enemigos

    def __repr__(self) -> str:
        return f"Sala({self.posicion}, {self.tipo!r}, {self.objetos}, {self.enemigos})"


# Entidad es la clase base de Personaje y Enemigo, asi las propiedades con sus validaciones se escriben una sola vez
class Entidad:
    def __init__(self, nombre: str, vida: int, ataque: int, defensa: int):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("el nombre debe ser un texto no vacío")
        self._nombre = valor

    @property
    def vida(self) -> int:
        return self._vida

    @vida.setter
    def vida(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DatoInvalidoError("la vida debe ser un número entero")
        if valor < 0:
            raise DatoInvalidoError("la vida no puede ser negativa")
        self._vida = valor

    @property
    def ataque(self) -> int:
        return self._ataque

    @ataque.setter
    def ataque(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DatoInvalidoError("el ataque debe ser un número entero")
        if valor < 0:
            raise DatoInvalidoError("el ataque no puede ser negativo")
        self._ataque = valor

    @property
    def defensa(self) -> int:
        return self._defensa

    @defensa.setter
    def defensa(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DatoInvalidoError("la defensa debe ser un número entero")
        if valor < 0:
            raise DatoInvalidoError("la defensa no puede ser negativa")
        self._defensa = valor

    def esta_vivo(self) -> bool:
        return self.vida > 0

    def recibir_dano(self, cantidad: int) -> None:
        # El daño debe ser un entero no negativo; no se usa para curar.
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise DatoInvalidoError("El daño debe ser un número entero")
        if cantidad < 0:
            raise DatoInvalidoError("El daño no puede ser negativo")

        # Evita que la vida quede por debajo de cero.
        self.vida = max(0, self.vida - cantidad)

    def atacar(self, objetivo: Entidad) -> int:
        # el daño es ataque - defensa, con un minimo de 1. Devuelve el daño hecho
        dano = max(1, self.ataque - objetivo.defensa)
        objetivo.recibir_dano(dano)
        return dano


class Enemigo(Entidad):
    # funcion para comparar objetos que tengan los mismos valores en distintas varaivles con (is), dando false
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Enemigo):
            return NotImplemented
        return (self.nombre, self.vida, self.ataque, self.defensa) == (
            other.nombre,
            other.vida,
            other.ataque,
            other.defensa,
        )

    def __repr__(self) -> str:
        return f"Enemigo({self.nombre!r}, {self.vida}, {self.ataque}, {self.defensa})"


class Goblin(Enemigo):
    """Ataque estándar, hereda atacar() de Enemigo sin cambios."""

    pass


class Orco(Enemigo):
    """Golpea más fuerte a costa de ignorar parte de su propia defensa al cargar."""

    def atacar(self, objetivo: Entidad) -> int:
        dano = max(1, (self.ataque + 2) - objetivo.defensa)
        objetivo.recibir_dano(dano)
        return dano


# PATRON FACTORY: es el unico sitio donde se decide que clase de enemigo se crea
# lo usan el generador y la carga desde json
TIPOS_ENEMIGO = {"Enemigo": Enemigo, "Goblin": Goblin, "Orco": Orco}


def crear_enemigo(tipo: str, nombre: str, vida: int, ataque: int, defensa: int) -> Enemigo:
    clase = TIPOS_ENEMIGO.get(tipo)
    if clase is None:
        raise DatoInvalidoError(f"Tipo de enemigo desconocido: {tipo!r}")
    return clase(nombre, vida, ataque, defensa)


class Objeto:
    # bonus = lo que suma al ataque del personaje mientras lo lleva equipado
    def __init__(self, nombre_o: str, tipo: str, descripcion_o: str, bonus: int = 0):
        self.nombre_o = nombre_o
        self.tipo = tipo
        self.descripcion_o = descripcion_o
        self.bonus = bonus

    @property
    def nombre_o(self) -> str:
        return self._nombre_o

    @nombre_o.setter
    def nombre_o(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("el nombre debe ser un texto no vacío")
        self._nombre_o = valor

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("El tipo no puede estar vacío")
        self._tipo = valor

    @property
    def descripcion_o(self):
        return self._descripcion_o

    @descripcion_o.setter
    def descripcion_o(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("La descripción no puede estar vacía")
        self._descripcion_o = valor

    @property
    def bonus(self) -> int:
        return self._bonus

    @bonus.setter
    def bonus(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise DatoInvalidoError("El bonus debe ser un entero no negativo")
        self._bonus = valor

    def __repr__(self) -> str:
        return f"Objeto({self.nombre_o!r}, {self.tipo!r}, {self.descripcion_o!r}, {self.bonus})"


class Personaje(Entidad):
    # el inventario es una lista pero solo cabe un objeto (el que lleva equipado)
    def __init__(
        self,
        nombre_p: str,
        vida: int,
        ataque: int,
        defensa: int,
        inventario: list[Objeto],
        oro: float = 0,
        vida_max: int | None = None,
    ):
        super().__init__(nombre_p, vida, ataque, defensa)
        if not isinstance(inventario, list) or not all(isinstance(o, Objeto) for o in inventario):
            raise DatoInvalidoError("El inventario debe ser una lista de objetos Objeto")
        if len(inventario) > 1:
            raise DatoInvalidoError("Solo se puede llevar un objeto")
        self.inventario = inventario
        self.vida_max = max(1, vida) if vida_max is None else vida_max
        if self.vida > self.vida_max:
            raise DatoInvalidoError("La vida no puede superar la vida máxima")
        self.oro = oro

    @property
    def vida_max(self) -> int:
        return self._vida_max

    @vida_max.setter
    def vida_max(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
            raise DatoInvalidoError("la vida máxima debe ser un entero positivo")
        self._vida_max = valor

    @property
    def oro(self) -> float:
        return self._oro

    @oro.setter
    def oro(self, valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
            raise DatoInvalidoError("el oro debe ser un número no negativo")
        self._oro = valor

    @property
    def objeto_equipado(self) -> Objeto | None:
        return self.inventario[0] if self.inventario else None

    @property
    def ataque_total(self) -> int:
        bonus = self.objeto_equipado.bonus if self.objeto_equipado else 0
        return self.ataque + bonus

    def equipar(self, objeto: Objeto) -> None:
        # solo un objeto: si ya llevaba otro, se pierde
        if not isinstance(objeto, Objeto):
            raise DatoInvalidoError("Solo se puede equipar un objeto Objeto")
        self.inventario = [objeto]

    def curar(self) -> None:
        self.vida = self.vida_max

    def atacar(self, objetivo: Entidad) -> int:
        # igual que Entidad.atacar pero usando el ataque con el bonus del arma
        dano = max(1, self.ataque_total - objetivo.defensa)
        objetivo.recibir_dano(dano)
        return dano

    def __repr__(self) -> str:
        return f"Personaje({self.nombre!r}, {self.vida}, {self.ataque}, {self.defensa}, {self.inventario})"


class Combate:
    # combate por turnos sin aleatoriedad, asi los resultados se pueden calcular a mano en los tests
    # PATRON OBSERVER: cada golpe se guarda en el registro y ademas se avisa a los observadores
    # (cualquier funcion que reciba un texto: logging, la interfaz, print...)
    def __init__(self, personaje: Personaje, enemigo: Enemigo, observadores=None):
        self.personaje = personaje
        self.enemigo = enemigo
        self.registro: list[str] = []  # aqui se guarda lo que pasa en cada turno
        self.observadores = list(observadores) if observadores else []

    def suscribir(self, observador) -> None:
        self.observadores.append(observador)

    def _emitir(self, evento: str) -> None:
        self.registro.append(evento)
        for observador in self.observadores:
            observador(evento)

    def ejecutar(self) -> bool:
        # lucha hasta que muera uno de los dos. Devuelve True si gana el personaje
        while self.personaje.esta_vivo() and self.enemigo.esta_vivo():
            dano = self.personaje.atacar(self.enemigo)
            self._emitir(f"{self.personaje.nombre} golpea a {self.enemigo.nombre}: -{dano}")
            # el enemigo solo contraataca si sigue vivo
            if self.enemigo.esta_vivo():
                dano = self.enemigo.atacar(self.personaje)
                self._emitir(f"{self.enemigo.nombre} golpea a {self.personaje.nombre}: -{dano}")
        return self.personaje.esta_vivo()


RUTA_NOMBRES = Path(__file__).parent / "nombres_mazmorras.txt"


def cargar_nombres(ruta: Path = RUTA_NOMBRES) -> list[str]:
    # un nombre por linea; se ignoran lineas vacias
    try:
        with open(ruta, encoding="utf-8") as f:
            nombres = [linea.strip() for linea in f if linea.strip()]
    except OSError as e:
        raise ErrorPersistencia(f"No se pudo leer {ruta}: {e}") from e
    if not nombres:
        raise ErrorPersistencia(f"El archivo {ruta} no contiene nombres")
    return nombres


NOMBRES_MAZMORRAS = cargar_nombres()

# El generador esta separado del modelo: las clases no saben nada de el, solo lo usa el juego
class GeneradorMazmorras:
    MIN_SALAS = 3  # entrada + una sala de objeto + una sala de enemigo
    MAX_SALAS = 8
    # catalogos pequeños: (tipo, nombre, vida, ataque, defensa) y (nombre, tipo, descripcion, bonus de ataque)
    ENEMIGOS = [
        ("Goblin", "Goblin", 10, 3, 1),
        ("Enemigo", "Esqueleto", 14, 4, 2),
        ("Orco", "Orco", 20, 5, 3),
    ]

    # ordenadas de peor a mejor arma
    ARMAS = [
        ("Espada oxidada", "arma", "Una espada vieja pero afilada", 1),
        ("Espada corta", "arma", "Ligera y fiable", 2),
        ("Hacha de guerra", "arma", "Pesada, pero hace mucho daño", 4),
        ("Espada rúnica", "arma", "Brilla con magia antigua", 6),
    ]

    def __init__(self, semilla: int | None = None):
        # random.Random(semilla): con la misma semilla sale siempre lo mismo
        self._rng = random.Random(semilla)

    def elegir_arma(self, posicion: int, total: int) -> tuple:
        # cuanto mas lejos de la entrada, mas pesan las armas buenas:
        # en la primera sala los pesos son 8-4-2-1 y en la ultima 1-2-4-8, y en medio se mezclan
        avance = posicion / max(1, total - 1)
        pesos = [(1 - avance) * (8 / 2**n) + avance * 2**n for n in range(len(self.ARMAS))]
        return self._rng.choices(self.ARMAS, weights=pesos)[0]

    def generar_sala(self, posicion: int, tipo: str, total: int) -> Sala:
        enemigos = []
        objetos = []
        if tipo == "enemigo":
            enemigos.append(crear_enemigo(*self._rng.choice(self.ENEMIGOS)))  # siempre instancias nuevas
        elif tipo == "objeto":
            objetos.append(Objeto(*self.elegir_arma(posicion, total)))
        return Sala(posicion, tipo, objetos, enemigos)

    def generar_mazmorra(self, nombre: str, num_salas: int) -> Mazmorra:
        if isinstance(num_salas, bool) or not isinstance(num_salas, int):
            raise DatoInvalidoError("El número de salas debe ser un entero")
        if num_salas < self.MIN_SALAS:
            raise DatoInvalidoError(
                f"la mazmorra necesita al menos {self.MIN_SALAS} salas (entrada, objeto y enemigo)"
            )
        # la entrada va siempre primera. Del resto, minimo una de objeto y una de enemigo, en cualquier orden
        tipos = ["objeto", "enemigo"]
        tipos += [self._rng.choice(["objeto", "enemigo"]) for _ in range(num_salas - 3)]
        self._rng.shuffle(tipos)
        salas = [self.generar_sala(0, "entrada", num_salas)]
        salas += [self.generar_sala(i, tipo, num_salas) for i, tipo in enumerate(tipos, start=1)]
        tesoro = round(self._rng.uniform(50, 500), 2)
        return Mazmorra(nombre, tesoro, salas)

    def generar_aleatoria(self, usados=()) -> Mazmorra:
        # el jugador no elige ni el nombre ni las salas: sale todo del generador
        libres = [n for n in NOMBRES_MAZMORRAS if n not in usados]
        nombre = self._rng.choice(libres or NOMBRES_MAZMORRAS)
        return self.generar_mazmorra(nombre, self._rng.randint(self.MIN_SALAS, self.MAX_SALAS))