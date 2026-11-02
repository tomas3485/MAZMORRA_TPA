# Mazmorra

Aplicación en Python para crear y gestionar aventuras de rol: campañas, mazmorras,
salas, enemigos, objetos y personajes.

Proyecto de la asignatura Técnicas de Programación Avanzada (Grado en Ingeniería
Informática, Universidad Nebrija).

## Grupo

- Tomas Lozano
- Luis Torrecilla
- Alberto Prieto
- Carlos Garcia-Mauriño

## Requisitos

- Python 3.10 o superior

## Instalación

```bash
git clone https://github.com/tomas3485/MAZMORRA_TPA.git
cd MAZMORRA_TPA
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt


Instalación
git clone https://github.com/tomas3485/MAZMORRA_TPA.git
cd MAZMORRA_TPA
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
Ejecución
python main.py
Estado actual (Práctica 2)
Modelo de dominio con herencia: Entidad es la clase base de Personaje y Enemigo; Enemigo se especializa en Goblin (ataque estándar) y Orco (daño aumentado, ignora parte de su propia defensa al cargar) — polimorfismo real: Combate llama a atacar() sin saber qué subtipo de enemigo es, y cada uno responde distinto.

Componentes:

Entidad / Personaje / Enemigo / Goblin / Orco: atributos (nombre, vida, ataque, defensa) encapsulados con @property y validación de tipo.
Sala, Mazmorra, Campaña: agregación (Campaña contiene Mazmorra, que contiene Sala, que contiene Enemigo y Objeto).
Combate: combate por turnos determinista (sin aleatoriedad, resultados calculables a mano).
GeneradorMazmorras: generación procedural con semilla reproducible.
La sala en posición 0 siempre es "entrada" y nunca tiene enemigos.
El resto de salas tienen 1-2 enemigos elegidos al azar entre Goblin, Esqueleto (Enemigo) y Orco.
Con la misma semilla (GeneradorMazmorras(semilla=N)), la mazmorra generada es siempre idéntica.
Pruebas
XX tests con pytest, cubriendo: creación de entidades, identidad vs. igualdad (is/==), el bug del argumento por defecto mutable, validaciones de tipo, daño y combate, polimorfismo entre tipos de enemigo, y generación procedural reproducible.

pytest test_modelo.py -v
Roadmap
Práctica 2: herencia, polimorfismo, excepciones. ✅
Práctica 3: patrones de diseño.
Práctica 4: interfaz gráfica y concurrencia.
Solo te queda un paso manual: cambia XX por el número real de tests (lo ves en la última línea de pytest test_modelo.py -v, tipo 23 passed).

Sigue pendiente tu respuesta para arrancar PRAC3: ¿JSON o SQLite para la persistencia?