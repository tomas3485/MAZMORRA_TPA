from modelo import Campaña, Mazmorra, Sala, Enemigo, Objeto, Personaje

def main() -> None:
    espada = Objeto("Espada oxidada", "arma", "Una espada vieja pero afilada")
    pocion = Objeto("Poción menor", "consumible", "Restaura algo de vida")

    goblin = Enemigo("Goblin", vida=10, ataque=3, defensa=1)

    heroe = Personaje("Aria", vida=30, ataque=5, defensa=2, inventario=[pocion])

    # Se crea la sala con objeto espada y enemigo goblin (ESTO HAY QUE HACERLO ALEATORIO!! En un futuro :))
    sala_entrada = Sala(
        posicion=(0, 0),
        tipo="entrada",
        objetos=[espada],
        enemigos=[goblin],
    )

    # Se crea la Mazmorra con esta Sala  
    mazmorra = Mazmorra("Cripta Olvidada", tesoro=150.0, salas=[sala_entrada])

    # Aqui se crea la campaña que contiene mazmorra
    campaña = Campaña(
        "Aventura Inicial",
        "Una primera incursión de prueba",
        mazmorras=[mazmorra],
    )

    # Este el flujo incial en el que se recorre la estruct
    print("=== Campaña ===")
    print(campaña)

    print("\n=== Mazmorras ===")
    for m in campaña.mazmorras:
        print(m)

        print("\n--- Salas ---")
        for sala in m.salas:
            print(sala)

    print("\n=== Personaje ===")
    print(heroe)

    print("\n¿Mazmorra despejada?", mazmorra.esta_despejada())


if __name__ == "__main__":
    main()