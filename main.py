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

class Mazmorra:
    def __init__(self, nombre_m: str, tesoro: float, salas: list[Sala]):
        self.nombre_m = nombre_m
        self.tesoro = tesoro
        self.salas = salas

    def valor_stock(self) -> float:
        return self.tesoro * self.tesoro

    def __repr__(self) -> str:
        return f"Mazmorra({self.nombre!r}, {self.tesoro}, {self.monstruo}, {self.salas})"

class Sala:
    def __init__(self, posicion: int, tipo: str, objetos: list[Objeto], enemigos: list[Enemigo]):
        self.posicion = posicion
        self.tipo = tipo
        self.objetos = objetos

class Enemigo:
    def __init__(self, nombre_o: str, vida: int, ataque: int, defensa: int):
        self.nombre_o = nombre_o
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa 
     
class Objeto:
    def __init__(self, nombre_o: str, tipo: str, descripcion_o: str):
        self.nombre_o = nombre_o
        self.tipo = tipo
        self.descripcion_o = descripcion_o 
