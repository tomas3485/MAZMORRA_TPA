# Mazmorra

Aplicación en Python para crear y jugar aventuras de rol: campañas, mazmorras,
salas, enemigos, objetos y personajes. Proyecto de Técnicas de Programación Avanzada
(Grado en Ingeniería Informática, Universidad Nebrija).

## Grupo

- Tomas Lozano
- Luis Torrecilla
- Alberto Prieto
- Carlos Garcia-Mauriño

## Instalación

```bash
git clone https://github.com/tomas3485/MAZMORRA_TPA.git
cd MAZMORRA_TPA
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
pip install -e .
```

Requiere Python 3.10 o superior.

## Uso

```bash
python -m mazmorra
```

- Se genera una campaña con mazmorras aleatorias.
- Se avanza sala a sala: salas de objeto (equipar arma) y salas de enemigo (combate por turnos).
- Si el personaje pierde, la mazmorra se reinicia. Si gana, cobra el tesoro y sube de nivel.
- La partida se guarda y se carga en `partida.json`.
- Todo lo que ocurre queda registrado en `mazmorra.log`.
- La campaña se puede exportar a JSON o Markdown.

Configuración opcional con variables de entorno: `MAZMORRA_DATOS` (fichero de partida),
`MAZMORRA_LOG` (nivel de log) y `MAZMORRA_LOGFILE` (fichero de log).

## Estructura (guía para desarrolladores)

| Fichero | Qué hace |
|---|---|
| `mazmorra/modelo.py` | Entidad, Personaje, Enemigo (Goblin, Orco), Objeto, Sala, Mazmorra, Campaña, Combate, GeneradorMazmorras y excepciones propias |
| `mazmorra/juego.py` | Lógica de la partida (clase `Juego`) y configuración del logging |
| `mazmorra/persistencia.py` | Guardar/cargar la partida en JSON y exportar a JSON o Markdown |
| `mazmorra/interfaz.py` | Interfaz gráfica con tkinter |
| `mazmorra/__main__.py` | Punto de entrada (`python -m mazmorra`) |
| `test_*.py` | Tests con pytest |

Patrones de diseño usados:
- **Factory:** `crear_enemigo` es el único sitio que decide qué clase de enemigo se crea.
- **Observer:** `Combate` y `Juego` avisan a sus suscriptores en cada evento (log, interfaz).
- **Strategy:** cada formato de exportación (`ExportadorJSON`, `ExportadorMarkdown`) es intercambiable.
- **Facade:** `Juego` coordina generador, combate, persistencia y exportación.

Otras decisiones:
- Excepciones propias: `ErrorMazmorra`, `DatoInvalidoError` (también es `ValueError`),
  `ErrorPersistencia` y `ErrorExportacion`.
- Guardado seguro: se escribe en un fichero temporal y luego se renombra, así no se pierde
  la partida si algo falla a medias.
- El JSON se trata como dato no fiable: se valida al cargarlo y nunca se ejecuta.
- La generación procedural es reproducible: con la misma semilla sale la misma mazmorra.

## Pruebas

```bash
python -m pytest
```

214 tests, con una cobertura real del 63% (se muestra al ejecutar pytest).
La interfaz gráfica (`interfaz.py`) y el punto de entrada (`__main__.py`) no tienen
tests automáticos: se prueban a mano.

## Estado

- Práctica 1: modelo de dominio ✅
- Práctica 2: herencia, polimorfismo y excepciones ✅
- Práctica 3: persistencia, logging, paquete, patrones, tests y documentación ✅
- Práctica 4: interfaz gráfica y concurrencia (pendiente)

- Licencia MIT (ver `LICENSE`).