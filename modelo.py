##############################################################################
"""███╗   ███╗ █████╗ ███████╗███╗   ███╗ ██████╗ ██████╗ ██████╗  █████╗
   ████╗ ████║██╔══██╗╚══███╔╝████╗ ████║██╔═══██╗╚════██╗██╔══██╗██╔══██╗
   ██╔████╔██║███████║  ███╔╝ ██╔████╔██║██║   ██║ █████╔╝██████╔╝███████║
   ██║╚██╔╝██║██╔══██║ ███╔╝  ██║╚██╔╝██║██║   ██║██╔═══╝ ██╔══██╗██╔══██║
   ██║ ╚═╝ ██║██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║██║  ██║
   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝"""
##############################################################################

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
    def __init__(self, posicion: int, tipo: str, objetos: list[Objeto], enemigos: list[Enemigo]):
        self.posicion = posicion
        self.tipo = tipo
        self.objetos = objetos
        self.enemigos = enemigos

    def __repr__(self) -> str:
        return f"Sala({self.posicion}, {self.tipo!r}, {self.objetos}, {self.enemigos})"

class Enemigo:
    def __init__(self, nombre_e: str, vida: int, ataque: int, defensa: int):
        self.nombre_e = nombre_e
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa 
        
    @property
    def nombre_e(self) -> str:
        return self._nombre_e

    @nombre_e.setter
    def nombre_e(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("el nombre no puede estar vacío")
        self._nombre_e = valor
    
    @property
    def vida(self) -> int:
        return self._vida

    @vida.setter
    def vida (self, valor: int) -> None:
        if valor < 0:
            raise ValueError("la vida no puede ser negativa")
        self._vida = valor

    @property
    def ataque(self) -> int:
        return self._ataque

    @ataque.setter
    def ataque (self, valor: int) -> None:
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

    #funcion para comparar objetos que tengan los mismos valores en distintas varaivles con (is), dando false
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Enemigo):
            return NotImplemented
        return (self.nombre_e, self.vida, self.ataque, self.defensa) == \
            (other.nombre_e, other.vida, other.ataque, other.defensa)

    def __repr__(self) -> str:
        return f"Enemigo({self.nombre_e!r}, {self.vida}, {self.ataque}, {self.defensa})"

            
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

class Personaje:
    def __init__(self,nombre_p:str,vida:int,ataque:int,defensa:int,inventario:list[Objeto]):
        self.nombre_p = nombre_p
        self.vida = vida
        self.ataque =ataque 
        self.defensa = defensa
        self.inventario = inventario

    @property
    def nombre_p(self) -> str:
        return self._nombre_p

    @nombre_p.setter
    def nombre_p(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("el nombre no puede estar vacío")
        self._nombre_p = valor

    @property
    def vida(self) -> int:
        return self._vida

    @vida.setter
    def vida (self, valor: int) -> None:
        if valor < 0:
            raise ValueError("la vida no puede ser negativa")
        self._vida = valor

    @property
    def ataque(self) -> int:
        return self._ataque

    @ataque.setter
    def ataque (self, valor: int) -> None:
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

    def __repr__(self) -> str:
        return f"Personaje({self.nombre_p!r}, {self.vida}, {self.ataque}, {self.defensa}, {self.inventario})"
