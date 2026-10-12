from __future__ import annotations  # sin esto Campaña da NameError porque usa Mazmorra antes de que este definida
import random


class Campaña:
    def __init__(self, nombre_c: str, descripcion: str, mazmorras: list[Mazmorra]):
        self.nombre_c = nombre_c
        self.descripcion = descripcion 
        self.mazmorras = mazmorras 

    def __repr__(self) -> str:
        return f"Campaña({self.nombre_c!r}, {self.descripcion!r}, {self.mazmorras})"

class Mazmorra:
    def __init__(self, nombre_m: str, tesoro: float, salas: list[Sala]):
        self.nombre_m = nombre_m
        self.tesoro = tesoro
        self.salas = salas

    @property
    def tesoro(self):
        return self._tesoro

    @tesoro.setter
    def tesoro(self, valor):
        if valor < 0:
            raise ValueError("El tesoro no puede ser negativo")
        self._tesoro = valor

    def enemigos_totales(self) -> list["Enemigo"]:
        return [e for sala in self.salas for e in sala.enemigos]

    def esta_despejada(self) -> bool:
        return not self.enemigos_totales()

    def __repr__(self) -> str:
        return f"Mazmorra({self.nombre_m!r}, {self.tesoro}, {self.salas})"

class Sala:
    # la posicion es un entero (orden de la sala dentro de la mazmorra)
    def __init__(self, posicion: int, tipo: str, objetos: list[Objeto], enemigos: list[Enemigo]):
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
        if not valor or not valor.strip():
            raise ValueError("el nombre no puede estar vacío")
        self._nombre = valor

    @property
    def vida(self) -> int:
        return self._vida

    @vida.setter
    def vida(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("la vida no puede ser negativa")
        self._vida = valor

    @property
    def ataque(self) -> int:
        return self._ataque

    @ataque.setter
    def ataque(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("el ataque no puede ser negativo")
        self._ataque = valor

    @property
    def defensa(self) -> int:
        return self._defensa

    @defensa.setter
    def defensa(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("la defensa no puede ser negativa")
        self._defensa = valor

    def esta_vivo(self) -> bool:
        return self.vida > 0

    def recibir_dano(self, cantidad: int) -> None:
        # max(0, ...) para que la vida no quede negativa (el setter lanzaria error)
        self.vida = max(0, self.vida - cantidad)

    def atacar(self, objetivo: Entidad) -> int:
        # el daño es ataque - defensa, con un minimo de 1. Devuelve el daño hecho
        dano = max(1, self.ataque - objetivo.defensa)
        objetivo.recibir_dano(dano)
        return dano


class Enemigo(Entidad):
    #funcion para comparar objetos que tengan los mismos valores en distintas varaivles con (is), dando false
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Enemigo):
            return NotImplemented
        return (self.nombre, self.vida, self.ataque, self.defensa) == \
            (other.nombre, other.vida, other.ataque, other.defensa)

    def __repr__(self) -> str:
        return f"Enemigo({self.nombre!r}, {self.vida}, {self.ataque}, {self.defensa})"

            
class Objeto:
    def __init__(self, nombre_o: str, tipo: str, descripcion_o: str):
        self.nombre_o = nombre_o
        self.tipo = tipo
        self.descripcion_o = descripcion_o

    @property
    def nombre_o(self) -> str:
            return self._nombre_o
    
    @nombre_o.setter
    def nombre_o(self, valor: str) -> None:
            if not valor or not valor.strip():
                raise ValueError("el nombre no puede estar vacío")
            self._nombre_o = valor

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El tipo no puede estar vacío")
        self._tipo = valor

    @property
    def descripcion_o(self):
        return self._descripcion_o

    @descripcion_o.setter
    def descripcion_o(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La descripción no puede estar vacía")
        self._descripcion_o = valor

    def __repr__(self) -> str:
        return f"Objeto({self.nombre_o!r}, {self.tipo!r}, {self.descripcion_o!r})"


class Personaje(Entidad):
    def __init__(self,nombre_p:str,vida:int,ataque:int,defensa:int,inventario:list[Objeto]):
        super().__init__(nombre_p, vida, ataque, defensa)
        self.inventario = inventario

    def __repr__(self) -> str:
        return f"Personaje({self.nombre!r}, {self.vida}, {self.ataque}, {self.defensa}, {self.inventario})"


class Combate:
    # combate por turnos sin aleatoriedad, asi los resultados se pueden calcular a mano en los tests
    def __init__(self, personaje: Personaje, enemigo: Enemigo):
        self.personaje = personaje
        self.enemigo = enemigo
        self.registro: list[str] = []  # aqui se guarda lo que pasa en cada turno

    def ejecutar(self) -> bool:
        # lucha hasta que muera uno de los dos. Devuelve True si gana el personaje
        while self.personaje.esta_vivo() and self.enemigo.esta_vivo():
            dano = self.personaje.atacar(self.enemigo)
            self.registro.append(f"{self.personaje.nombre} golpea a {self.enemigo.nombre}: -{dano}")
            # el enemigo solo contraataca si sigue vivo
            if self.enemigo.esta_vivo():
                dano = self.enemigo.atacar(self.personaje)
                self.registro.append(f"{self.enemigo.nombre} golpea a {self.personaje.nombre}: -{dano}")
        return self.personaje.esta_vivo()


# El generador esta separado del modelo: las clases no saben nada de el, solo lo usa main
class GeneradorMazmorras:
    # catalogos pequeños: (nombre, vida, ataque, defensa) y (nombre, tipo, descripcion)
    ENEMIGOS = [("Goblin", 10, 3, 1), ("Esqueleto", 14, 4, 2), ("Orco", 20, 5, 3)]
    OBJETOS = [("Espada oxidada", "arma", "Una espada vieja pero afilada"),
               ("Poción menor", "consumible", "Restaura algo de vida")]

    def __init__(self, semilla: int | None = None):
        # random.Random(semilla): con la misma semilla sale siempre lo mismo
        self._rng = random.Random(semilla)

    def generar_sala(self, posicion: int) -> Sala:
        # la primera sala es la entrada y no tiene enemigos
        tipo = "entrada" if posicion == 0 else "normal"
        num_enemigos = 0 if posicion == 0 else self._rng.randint(1, 2)
        enemigos = [Enemigo(*self._rng.choice(self.ENEMIGOS)) for _ in range(num_enemigos)]  # siempre instancias nuevas
        objetos = [Objeto(*self._rng.choice(self.OBJETOS)) for _ in range(self._rng.randint(0, 1))]
        return Sala(posicion, tipo, objetos, enemigos)

    def generar_mazmorra(self, nombre: str, num_salas: int) -> Mazmorra:
        if num_salas < 1:
            raise ValueError("la mazmorra necesita al menos una sala")
        salas = [self.generar_sala(i) for i in range(num_salas)]
        tesoro = round(self._rng.uniform(50, 500), 2)
        return Mazmorra(nombre, tesoro, salas)