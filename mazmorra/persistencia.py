import json
import logging
import os
import tempfile
from abc import ABC, abstractmethod

from .modelo import (
    Campaña,
    DatoInvalidoError,
    ErrorExportacion,
    ErrorPersistencia,
    Mazmorra,
    Objeto,
    Personaje,
    Sala,
    crear_enemigo,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Paso de objetos a diccionarios (y vuelta)
# ---------------------------------------------------------------------


def objeto_a_dict(o: Objeto) -> dict:
    return {"nombre_o": o.nombre_o, "tipo": o.tipo, "descripcion_o": o.descripcion_o, "bonus": o.bonus}


def personaje_a_dict(p: Personaje) -> dict:
    return {
        "nombre": p.nombre,
        "vida": p.vida,
        "vida_max": p.vida_max,
        "ataque": p.ataque,
        "defensa": p.defensa,
        "oro": p.oro,
        "inventario": [objeto_a_dict(o) for o in p.inventario],
    }


def campana_a_dict(campana: Campaña) -> dict:
    return {
        "nombre": campana.nombre_c,
        "descripcion": campana.descripcion,
        "mazmorras": [
            {
                "nombre": m.nombre_m,
                "tesoro": m.tesoro,
                "progreso": m.progreso,
                "salas": [
                    {
                        "posicion": s.posicion,
                        "tipo": s.tipo,
                        "objetos": [objeto_a_dict(o) for o in s.objetos],
                        "enemigos": [
                            {
                                "clase": type(e).__name__,  # para volver a crear la subclase correcta
                                "nombre": e.nombre,
                                "vida": e.vida,
                                "ataque": e.ataque,
                                "defensa": e.defensa,
                            }
                            for e in s.enemigos
                        ],
                    }
                    for s in m.salas
                ],
            }
            for m in campana.mazmorras
        ],
    }


def personaje_desde_dict(d: dict) -> Personaje:
    inventario = [Objeto(**o) for o in d["inventario"]]
    return Personaje(d["nombre"], d["vida"], d["ataque"], d["defensa"], inventario, d["oro"], d["vida_max"])


def campana_desde_dict(datos: dict) -> Campaña:
    mazmorras = []
    for m in datos["mazmorras"]:
        salas = []
        for s in m["salas"]:
            objetos = [Objeto(**o) for o in s["objetos"]]
            enemigos = [
                crear_enemigo(e["clase"], e["nombre"], e["vida"], e["ataque"], e["defensa"])
                for e in s["enemigos"]
            ]
            salas.append(Sala(s["posicion"], s["tipo"], objetos, enemigos))
        mazmorras.append(Mazmorra(m["nombre"], m["tesoro"], salas, m["progreso"]))
    return Campaña(datos["nombre"], datos["descripcion"], mazmorras)


# ---------------------------------------------------------------------
# Guardar y cargar la partida
# ---------------------------------------------------------------------


def escribir_seguro(ruta: str, texto: str) -> None:
    # "w" trunca el fichero: si algo falla a medias se pierde todo. Por eso se escribe en un
    # temporal y luego se renombra, el original solo se cambia cuando ya esta todo escrito
    directorio = os.path.dirname(os.path.abspath(ruta))
    try:
        fd, temporal = tempfile.mkstemp(dir=directorio, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(texto)
            os.replace(temporal, ruta)
        except BaseException:
            if os.path.exists(temporal):
                os.remove(temporal)
            raise
    except OSError as error:
        raise ErrorPersistencia(f"No se pudo escribir '{ruta}': {error}") from error


def guardar_partida(ruta: str, personaje: Personaje, campana: Campaña, completadas: int) -> None:
    datos = {
        "personaje": personaje_a_dict(personaje),
        "campana": campana_a_dict(campana),
        "completadas": completadas,
    }
    escribir_seguro(ruta, json.dumps(datos, ensure_ascii=False, indent=2))
    logger.info("Partida de %s guardada en %s", personaje.nombre, ruta)


def cargar_partida(ruta: str) -> tuple[Personaje, Campaña, int]:
    # si el fichero no existe sube FileNotFoundError (el juego lo usa para saber que es la primera vez)
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        logger.error("JSON no válido en %s: %s", ruta, error)
        raise ErrorPersistencia(f"'{ruta}' no es un JSON válido: {error}") from error
    except OSError as error:
        logger.error("No se pudo leer %s: %s", ruta, error)
        raise ErrorPersistencia(f"No se pudo leer '{ruta}': {error}") from error

    if not isinstance(datos, dict):
        raise ErrorPersistencia(f"'{ruta}' no contiene una partida")
    try:
        completadas = datos["completadas"]
        if isinstance(completadas, bool) or not isinstance(completadas, int) or completadas < 0:
            raise DatoInvalidoError("completadas debe ser un entero no negativo")
        personaje = personaje_desde_dict(datos["personaje"])
        campana = campana_desde_dict(datos["campana"])
    except (KeyError, TypeError, DatoInvalidoError) as error:
        logger.error("Datos no válidos en %s: %r", ruta, error)
        raise ErrorPersistencia(f"Datos de partida no válidos: {error!r}") from error
    logger.info("Partida de %s cargada desde %s", personaje.nombre, ruta)
    return personaje, campana, completadas


# ---------------------------------------------------------------------
# Exportacion (PATRON STRATEGY: cada formato es una estrategia intercambiable)
# ---------------------------------------------------------------------


class Exportador(ABC):
    @abstractmethod
    def exportar(self, campana: Campaña) -> str:
        pass


class ExportadorJSON(Exportador):
    def exportar(self, campana: Campaña) -> str:
        return json.dumps(campana_a_dict(campana), ensure_ascii=False, indent=2)


class ExportadorMarkdown(Exportador):
    def exportar(self, campana: Campaña) -> str:
        lineas = [f"# {campana.nombre_c}", "", campana.descripcion, ""]
        for m in campana.mazmorras:
            lineas += [f"## {m.nombre_m} (tesoro: {m.tesoro})", ""]
            for s in m.salas:
                lineas.append(f"### Sala {s.posicion} ({s.tipo})")
                for o in s.objetos:
                    lineas.append(f"- Objeto: {o.nombre_o} (+{o.bonus} ataque)")
                for e in s.enemigos:
                    lineas.append(f"- Enemigo: {e.nombre}, vida {e.vida}, ataque {e.ataque}, defensa {e.defensa}")
                lineas.append("")
        return "\n".join(lineas)


EXPORTADORES = {"json": ExportadorJSON(), "md": ExportadorMarkdown()}


def exportar_campana(campana: Campaña, formato: str, ruta: str) -> None:
    exportador = EXPORTADORES.get(formato)
    if exportador is None:
        raise ErrorExportacion(f"Formato desconocido: {formato!r} (disponibles: {sorted(EXPORTADORES)})")
    try:
        escribir_seguro(ruta, exportador.exportar(campana))
    except ErrorPersistencia as error:
        raise ErrorExportacion(str(error)) from error
    logger.info("Campaña exportada a %s (%s)", ruta, formato)
