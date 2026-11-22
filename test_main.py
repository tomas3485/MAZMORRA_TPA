import json

import pytest

from mazmorra.__main__ import main


def test_main_consola_crea_partida_juega_y_guarda(tmp_path, monkeypatch, capsys):
    # Ejecuta el modo consola desde cero y comprueba que se crea el archivo
    # de guardado y que se muestra el mensaje "Guardado en".
    monkeypatch.chdir(tmp_path)
    ruta = str(tmp_path / "partida.json")

    codigo = main(["--consola", "--archivo", ruta, "--semilla", "1", "--nombre", "Test"])

    assert codigo == 0
    assert (tmp_path / "partida.json").exists()
    salida = capsys.readouterr().out
    assert "Guardado en" in salida


def test_main_consola_exporta_markdown(tmp_path, monkeypatch):
    # Comprueba que la opción --exportar md genera el archivo campana.md.
    monkeypatch.chdir(tmp_path)
    ruta = str(tmp_path / "partida.json")

    main(["--consola", "--archivo", ruta, "--semilla", "2", "--exportar", "md"])

    assert (tmp_path / "campana.md").exists()


def test_main_consola_continua_una_partida_guardada(tmp_path, monkeypatch):
    # Ejecuta el juego dos veces con el mismo archivo y verifica que la segunda
    # carga la partida existente (mismo personaje y progreso) en vez de crear una nueva.
    monkeypatch.chdir(tmp_path)
    ruta = str(tmp_path / "partida.json")

    main(["--consola", "--archivo", ruta, "--semilla", "3", "--nombre", "Primero"])
    with open(ruta, encoding="utf-8") as f:
        completadas_antes = json.load(f)["completadas"]

    # segunda ejecución: debe cargar la partida existente, no crear "Heroe" de cero
    main(["--consola", "--archivo", ruta, "--semilla", "3"])
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)

    assert datos["personaje"]["nombre"] == "Primero"
    assert datos["completadas"] >= completadas_antes


def test_main_consola_genera_mazmorra_si_la_partida_cargada_no_tiene(tmp_path, monkeypatch):
    # Carga una partida guardada sin mazmorras y comprueba que el programa
    # no falla: genera una nueva antes de jugar y termina con código 0.
    # partida guardada con 0 mazmorras pendientes: demo_consola debe generar una antes de jugar
    monkeypatch.chdir(tmp_path)
    ruta = tmp_path / "partida.json"
    ruta.write_text(
        json.dumps(
            {
                "personaje": {
                    "nombre": "Sin Mazmorras",
                    "vida": 30,
                    "vida_max": 30,
                    "ataque": 5,
                    "defensa": 2,
                    "oro": 0,
                    "inventario": [],
                },
                "campana": {"nombre": "Camp", "descripcion": "Desc", "mazmorras": []},
                "completadas": 0,
            }
        ),
        encoding="utf-8",
    )

    codigo = main(["--consola", "--archivo", str(ruta), "--semilla", "1"])

    assert codigo == 0


def test_main_version(capsys):
    # Comprueba que --version muestra el nombre del programa y sale con código 0.
    with pytest.raises(SystemExit) as salida:
        main(["--version"])

    assert salida.value.code == 0
    assert "mazmorra" in capsys.readouterr().out


def test_main_devuelve_1_si_la_partida_esta_corrupta(tmp_path, monkeypatch, capsys):
    # Si el archivo de guardado no es un JSON válido, main debe devolver 1
    # y mostrar un mensaje "Error:" por la salida de errores.
    monkeypatch.chdir(tmp_path)
    ruta = tmp_path / "partida.json"
    ruta.write_text("{esto no es json", encoding="utf-8")

    codigo = main(["--consola", "--archivo", str(ruta)])

    assert codigo == 1
    assert "Error:" in capsys.readouterr().err


def test_main_sin_consola_lanza_la_interfaz_grafica(tmp_path, monkeypatch):
    # Sin --consola, main debe lanzar la interfaz gráfica. Se sustituye `lanzar`
    # por una función falsa para comprobar que se llama una sola vez.
    monkeypatch.chdir(tmp_path)
    llamadas = []
    monkeypatch.setattr("mazmorra.interfaz.lanzar", lambda juego: llamadas.append(juego))

    codigo = main(["--archivo", str(tmp_path / "partida.json")])

    assert codigo == 0
    assert len(llamadas) == 1