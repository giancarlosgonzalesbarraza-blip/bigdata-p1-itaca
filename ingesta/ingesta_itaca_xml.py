import os
import hashlib
import json
import logging
import xml.etree.ElementTree as ET
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingesta_itaca_xml")

DIR_RAIZ = "Analisis_Academico"
ANIOS = sorted(
    d for d in os.listdir(DIR_RAIZ)
    if os.path.isdir(os.path.join(DIR_RAIZ, d))
)

TABLAS = ["alumnos", "cursos", "calificaciones", "contenidos"]

# Etiqueta XML de cada registro (singular) dentro del contenedor plural
REGISTRO = {
    "alumnos": "alumno",
    "cursos": "curso",
    "calificaciones": "calificacion",
    "contenidos": "contenido",
}

# Atributo del XML -> campo del modelo de datos
MAPA = {
    "alumnos": {
        "NIA": "NIA",
        "curso": "Curso",
        "turno": "Turno",
        "grupo": "Grupo",
        # PrimSeg, Ciclo, Grado y Familia no aparecen en el XML exportado
    },
    "cursos": {
        "codigo": "Codigo",
        "nombre_cas": "Nombre_Cas",
        "nombre_val": "Nombre_Val",
        "padre": "Padre",
    },
    "calificaciones": {
        "alumno": "NIA",
        "curso": "Curso",
        "contenido": "Modulo",
        "nota_numerica": "Nota",
        "evaluacion": "Evaluacion",
    },
    "contenidos": {
        "curso": "Curso",
        "codigo": "Modulo",
        "nombre_cas": "Nombre_Modulo",
    },
}

# Campos del modelo (su orden define el orden de las claves en el JSON)
CAMPOS = {
    "alumnos": ["Anyo", "NIA", "Curso", "PrimSeg", "Ciclo", "Grado", "Familia", "Turno", "Grupo"],
    "cursos": ["Anyo", "Codigo", "Nombre_Cas", "Nombre_Val", "Padre"],
    "calificaciones": ["Anyo", "NIA", "Curso", "Modulo", "Nota", "Evaluacion"],
    "contenidos": ["Anyo", "Curso", "Modulo", "Nombre_Modulo"],
}

def anonimizar_nia(nia: str) -> str:
    """Seudonimiza el NIA con SHA-256 truncado. Determinista: un mismo NIA
    produce siempre el mismo identificador (permite cruzar tablas y años)."""
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]

def parsear_xml(anyo: str, tabla: str) -> list[dict]:
    ruta = f"{DIR_RAIZ}/{anyo}/{tabla}.xml"
    arbol = ET.parse(ruta)
    raiz = arbol.getroot()

    # Estructura real: <centro> -> <alumnos> -> <alumno .../> (datos en atributos)
    registros = []
    for nodo in raiz.findall(f"./{tabla}/{REGISTRO[tabla]}"):
        valores = {"Anyo": anyo}  # el año académico viene del snapshot, no del registro
        valores.update({campo: nodo.get(atributo) for atributo, campo in MAPA[tabla].items()})
        if valores.get("NIA") is not None:
            valores["NIA"] = anonimizar_nia(valores["NIA"])
        registros.append({campo: valores.get(campo) for campo in CAMPOS[tabla]})
    return registros

def guardar(datos: list[dict], nombre: str, anyo: str) -> None:
    fecha = date.today().isoformat()
    ruta = f"data/raw/{anyo}/{nombre}_{fecha}.json"
    os.makedirs(f"data/raw/{anyo}", exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    logger.info("Guardados %d registros en %s", len(datos), ruta)

if __name__ == "__main__":
    for anyo in ANIOS:
        for tabla in TABLAS:
            guardar(parsear_xml(anyo, tabla), tabla, anyo)
