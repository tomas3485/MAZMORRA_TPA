import json
import os

import pytest

from mazmorra.modelo import (
    Campaña,
    DatoInvalidoError,
    ErrorExportacion,
    ErrorPersistencia,
    Mazmorra,
    Objeto,
    Orco,
    Personaje,
    Sala,
)
from mazmorra.persistencia import (
    ExportadorJSON,
    ExportadorMarkdown,
    campana_a_dict,
    campana_desde_dict,
    cargar_partida,
    escribir_seguro,
    exportar_campana,
    guardar_partida,
    objeto_a_dict,
    personaje_a_dict,
    personaje_desde_dict,
)


def campana_ejemplo():
    # Datos de apoyo: crea una campaña con una mazmorra de tres salas (entrada, objeto y enemigo).
    salas = [
        Sala(0, "entrada", [], []),
        Sala(1, "objeto", [Objeto("Espada", "arma", "Una espada", 2)], []),
        Sala(2, "enemigo", [], [Orco("Orco", 20, 5, 3)]),
    ]
    return Campaña("Aventura", "Descripción", [Mazmorra("Cripta", 100.0, salas)])


def personaje_ejemplo():
    # Datos de apoyo: crea un personaje con una espada equipada, oro y vida máxima.
    espada = Objeto("Espada", "arma", "Una espada", 3)
    return Personaje("Aria", 30, 5, 2, [espada], oro=10.5, vida_max=40)


# ---------------------------------------------------------------------
# Diccionarios
# ---------------------------------------------------------------------


def test_objeto_a_dict():
    # Comprueba que un objeto se convierte al diccionario esperado.
    assert objeto_a_dict(Objeto("Espada", "arma", "Una espada", 3)) == {
        "nombre_o": "Espada",
        "tipo": "arma",
        "descripcion_o": "Una espada",
        "bonus": 3,
    }


def test_personaje_ida_y_vuelta():
    # Convertir un personaje a dict y volver a crearlo no pierde datos.
    original = personaje_a_dict(personaje_ejemplo())

    copia = personaje_desde_dict(original)

    assert personaje_a_dict(copia) == original


def test_campana_ida_y_vuelta():
    # Lo mismo para una campaña completa: dict -> campaña -> dict da el mismo resultado.
    original = campana_a_dict(campana_ejemplo())

    copia = campana_desde_dict(original)

    assert campana_a_dict(copia) == original


def test_la_campana_cargada_conserva_el_subtipo_de_enemigo():
    # Al reconstruir la campaña, el enemigo sigue siendo un Orco (no un Enemigo genérico).
    copia = campana_desde_dict(campana_a_dict(campana_ejemplo()))

    enemigo = copia.mazmorras[0].salas[2].enemigos[0]

    assert type(enemigo) is Orco


# ---------------------------------------------------------------------
# escribir_seguro
# ---------------------------------------------------------------------


def test_escribir_seguro_escribe_y_no_deja_temporales(tmp_path):
    # Escribe el contenido en el fichero y no deja archivos temporales sobrantes.
    ruta = tmp_path / "datos.txt"

    escribir_seguro(str(ruta), "hola")

    assert ruta.read_text(encoding="utf-8") == "hola"
    assert [p.name for p in tmp_path.iterdir()] == ["datos.txt"]


def test_escribir_seguro_en_carpeta_inexistente_lanza_error_propio(tmp_path):
    # Si la carpeta de destino no existe, se lanza ErrorPersistencia.
    with pytest.raises(ErrorPersistencia):
        escribir_seguro(str(tmp_path / "no_existe" / "datos.txt"), "hola")


def test_si_falla_el_renombrado_se_conserva_el_original_y_se_borra_el_temporal(tmp_path, monkeypatch):
    # Simula un fallo al renombrar: el fichero original queda intacto y el temporal se elimina.
    ruta = tmp_path / "datos.txt"
    ruta.write_text("original", encoding="utf-8")

    def falla(origen, destino):
        raise OSError("fallo simulado")

    monkeypatch.setattr(os, "replace", falla)

    with pytest.raises(ErrorPersistencia):
        escribir_seguro(str(ruta), "nuevo")

    assert ruta.read_text(encoding="utf-8") == "original"
    assert [p.name for p in tmp_path.iterdir()] == ["datos.txt"]


# ---------------------------------------------------------------------
# Guardar y cargar partida
# ---------------------------------------------------------------------


def test_guardar_y_cargar_partida(tmp_path):
    # Guarda una partida y comprueba que al cargarla personaje, campaña y progreso coinciden.
    ruta = str(tmp_path / "partida.json")
    guardar_partida(ruta, personaje_ejemplo(), campana_ejemplo(), 2)

    personaje, campana, completadas = cargar_partida(ruta)

    assert personaje_a_dict(personaje) == personaje_a_dict(personaje_ejemplo())
    assert campana_a_dict(campana) == campana_a_dict(campana_ejemplo())
    assert completadas == 2


def test_cargar_sin_fichero_lanza_file_not_found(tmp_path):
    # Si el archivo no existe, se lanza FileNotFoundError (así se sabe que no hay partida).
    with pytest.raises(FileNotFoundError):
        cargar_partida(str(tmp_path / "no_existe.json"))


def test_cargar_json_roto_lanza_error_propio(tmp_path):
    # Un JSON mal formado lanza ErrorPersistencia.
    ruta = tmp_path / "partida.json"
    ruta.write_text("{no es json", encoding="utf-8")

    with pytest.raises(ErrorPersistencia):
        cargar_partida(str(ruta))


def test_cargar_fichero_con_bytes_invalidos_lanza_error_propio(tmp_path):
    # Un fichero con bytes que no son texto válido lanza ErrorPersistencia.
    ruta = tmp_path / "partida.json"
    ruta.write_bytes(b"\xff\xfe\xfa")

    with pytest.raises(ErrorPersistencia):
        cargar_partida(str(ruta))


def test_cargar_una_carpeta_lanza_error_propio(tmp_path):
    # Si la ruta es una carpeta en vez de un archivo, lanza ErrorPersistencia.
    with pytest.raises(ErrorPersistencia):
        cargar_partida(str(tmp_path))


def test_cargar_json_que_no_es_un_diccionario_lanza_error_propio(tmp_path):
    # Un JSON válido pero que no es un diccionario (aquí una lista) se rechaza.
    ruta = tmp_path / "partida.json"
    ruta.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(ErrorPersistencia):
        cargar_partida(str(ruta))


def test_cargar_partida_incompleta_lanza_error_propio(tmp_path):
    # Si faltan datos obligatorios (personaje, campaña), lanza ErrorPersistencia.
    ruta = tmp_path / "partida.json"
    ruta.write_text('{"completadas": 1}', encoding="utf-8")

    with pytest.raises(ErrorPersistencia):
        cargar_partida(str(ruta))


def _partida_guardada_con(tmp_path, cambio):
    # Auxiliar: guarda una partida válida, le aplica una modificación (corrupción) y devuelve su ruta.
    ruta = tmp_path / "partida.json"
    guardar_partida(str(ruta), personaje_ejemplo(), campana_ejemplo(), 1)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    cambio(datos)
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return str(ruta)


@pytest.mark.parametrize("completadas", [-1, True, "1", 1.5])
def test_cargar_con_completadas_invalido_lanza_error_propio(tmp_path, completadas):
    # "completadas" debe ser un entero no negativo; otros valores lanzan ErrorPersistencia.
    ruta = _partida_guardada_con(tmp_path, lambda d: d.update(completadas=completadas))

    with pytest.raises(ErrorPersistencia):
        cargar_partida(ruta)


def test_cargar_con_datos_invalidos_en_el_personaje_lanza_error_propio(tmp_path):
    # Si el personaje guardado tiene datos inválidos (vida negativa), la carga falla con ErrorPersistencia.
    ruta = _partida_guardada_con(tmp_path, lambda d: d["personaje"].update(vida=-5))

    with pytest.raises(ErrorPersistencia):
        cargar_partida(ruta)


# ---------------------------------------------------------------------
# Exportación (patrón Strategy)
# ---------------------------------------------------------------------


def test_exportador_json_devuelve_la_campana_como_json():
    # El exportador JSON genera un texto que, al leerlo, equivale al diccionario de la campaña.
    texto = ExportadorJSON().exportar(campana_ejemplo())

    assert json.loads(texto) == campana_a_dict(campana_ejemplo())


def test_exportador_markdown_incluye_mazmorras_objetos_y_enemigos():
    # El exportador Markdown genera títulos, salas, objetos y enemigos con el formato esperado.
    texto = ExportadorMarkdown().exportar(campana_ejemplo())

    assert texto.startswith("# Aventura")
    assert "## Cripta (tesoro: 100.0)" in texto
    assert "### Sala 1 (objeto)" in texto
    assert "- Objeto: Espada (+2 ataque)" in texto
    assert "- Enemigo: Orco" in texto


@pytest.mark.parametrize("formato, extension", [("json", "json"), ("md", "md")])
def test_exportar_campana_crea_el_fichero(tmp_path, formato, extension):
    # exportar_campana elige el exportador según el formato y escribe un archivo no vacío.
    ruta = tmp_path / f"campana.{extension}"

    exportar_campana(campana_ejemplo(), formato, str(ruta))

    assert ruta.read_text(encoding="utf-8") != ""


def test_exportar_formato_desconocido_lanza_error_propio(tmp_path):
    # Un formato no soportado (pdf) lanza ErrorExportacion.
    with pytest.raises(ErrorExportacion):
        exportar_campana(campana_ejemplo(), "pdf", str(tmp_path / "campana.pdf"))


def test_exportar_en_carpeta_inexistente_lanza_error_propio(tmp_path):
    # Si la carpeta de destino no existe, la exportación lanza ErrorExportacion.
    with pytest.raises(ErrorExportacion):
        exportar_campana(campana_ejemplo(), "md", str(tmp_path / "no_existe" / "campana.md"))