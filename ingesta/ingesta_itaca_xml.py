import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

# Carpetas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
FUENTE = BASE_DIR / "data" / "Analisis_Academico"
DESTINO = BASE_DIR / "data" / "raw"

TABLAS = {
    "alumnos.xml": {
        "registro": "alumno",
        "campos": {"NIA": "NIA", "curso": "Curso", "turno": "Turno", "grupo": "Grupo"},
        "modelo": ["Anyo", "NIA", "Curso", "PrimSeg", "Ciclo", "Grado", "Familia", "Turno", "Grupo"],
    },
    "cursos.xml": {
        "registro": "curso",
        "campos": {"codigo": "Codigo", "nombre_cas": "Nombre_Cas",
                   "nombre_val": "Nombre_Val", "padre": "Padre"},
        "modelo": ["Anyo", "Codigo", "Nombre_Cas", "Nombre_Val", "Padre"],
    },
    "calificaciones.xml": {
        "registro": "calificacion",
        "campos": {"alumno": "NIA", "curso": "Curso", "contenido": "Modulo",
                   "nota_numerica": "Nota", "evaluacion": "Evaluacion"},
        "modelo": ["Anyo", "NIA", "Curso", "Modulo", "Nota", "Evaluacion"],
    },
    "contenidos.xml": {
        "registro": "contenido",
        "campos": {"curso": "Curso", "codigo": "Modulo", "nombre_cas": "Nombre_Modulo"},
        "modelo": ["Anyo", "Curso", "Modulo", "Nombre_Modulo"],
    },
}


def anonimizar_nia(nia: str) -> str:
    """Seudonimiza el NIA con SHA-256 truncado. Determinista: un mismo NIA
    produce siempre el mismo identificador (permite cruzar tablas y años)."""
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]


def parsear_xml(ruta_xml: Path, config: dict, anyo: str) -> list:
    """Lee un XML y devuelve una lista de registros (dicts) listos para JSON."""
    raiz = ET.parse(ruta_xml).getroot()

    registros = []
    for registro in raiz.findall(f".//{config['registro']}"):
        fila = {"Anyo": anyo}
        for atributo, campo in config["campos"].items():
            fila[campo] = registro.get(atributo)

        # Se anonimiza en alumnos y calificaciones (las que tienen NIA)
        if fila.get("NIA") is not None:
            fila["NIA"] = anonimizar_nia(fila["NIA"])

        # Respeta el orden y los campos del modelo (los ausentes quedan en None)
        registros.append({campo: fila.get(campo) for campo in config["modelo"]})
    return registros


def main():
    total_registros = 0

    for carpeta in sorted(FUENTE.iterdir()):
        if not carpeta.is_dir():
            continue

        anyo = carpeta.name
        salida_curso = DESTINO / anyo
        salida_curso.mkdir(parents=True, exist_ok=True)

        for nombre_xml, config in TABLAS.items():
            ruta_xml = carpeta / nombre_xml
            if not ruta_xml.exists():
                print(f"  ! falta {ruta_xml}, lo salto")
                continue

            registros = parsear_xml(ruta_xml, config, anyo)

            tabla = nombre_xml.removesuffix(".xml")
            ruta_json = salida_curso / f"{tabla}.json"
            ruta_json.write_text(
                json.dumps(registros, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            total_registros += len(registros)
            print(f"  {anyo}/{nombre_xml} -> {ruta_json.relative_to(BASE_DIR)}  ({len(registros)} registros)")

    print(f"Total registros ingestados: {total_registros}")


if __name__ == "__main__":
    main()