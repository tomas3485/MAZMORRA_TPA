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
```

## Ejecución

```bash
python main.py
```

## Pruebas

```bash
pytest test_modelo.py -v
```

## Estado actual (Práctica 1)

Modelo de dominio: clases `Campaña`, `Mazmorra`, `Sala`, `Enemigo`, `Objeto` y
`Personaje`, con encapsulamiento mediante `@property`, comparación por igualdad
(`__eq__`) y pruebas unitarias con `pytest`.

## Roadmap

- Práctica 2: herencia, polimorfismo, excepciones.
- Práctica 3: patrones de diseño.
- Práctica 4: interfaz gráfica y concurrencia.