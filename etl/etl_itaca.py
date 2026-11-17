import json
import logging
import os

import pandas as pd
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("etl_itaca")

DIR_RAW = "data/raw"
DIR_SALIDA = "data/processed"
MONGO_URI = "mongodb://localhost:27017"
DB = "academico"
TABLAS = ["alumnos", "cursos", "calificaciones", "contenidos"]

def ultimas_rutas_raw(carpeta_anyo: str, tabla: str) -> list[str]:
    """Devuelve las rutas del JSON mas reciente de una tabla en un año."""
    return [os.path.join(carpeta_anyo, f)
            for f in sorted(os.listdir(carpeta_anyo))
            if f.startswith(f"{tabla}_") and f.endswith(".json")]

def limpiar(df: pd.DataFrame, tabla: str) -> pd.DataFrame:
    n_antes = len(df)

    # Duplicados exactos (misma fila completa, incluido Anyo)
    df = df.drop_duplicates().reset_index(drop=True)

    # Textos: quitar espacios y convertir cadenas vacias a nulo
    for col in df.columns:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

    # Nota -> float valido en [0, 10]; fuera de rango o no numerico -> nulo
    if "Nota" in df.columns:
        df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")
        invalidas = ((df["Nota"] < 0) | (df["Nota"] > 10)).sum()
        df.loc[(df["Nota"] < 0) | (df["Nota"] > 10), "Nota"] = pd.NA
        if invalidas:
            logger.warning("%s: %d notas fuera de rango [0,10] -> nulo", tabla, invalidas)

    # Codigos ( Curso, Modulo, Codigo, Padre ) SIEMPRE como texto para no perder ceros a la izquierda
    for col in ("Curso", "Modulo", "Codigo", "Padre", "NIA"):
        if col in df.columns:
            df[col] = df[col].astype("string")

    logger.info("%s: %d registros -> %d tras limpieza", tabla, n_antes, len(df))
    return df

def guardar(df: pd.DataFrame, anyo: str, tabla: str) -> None:
    ruta_dir = f"{DIR_SALIDA}/{anyo}"
    os.makedirs(ruta_dir, exist_ok=True)
    ruta = f"{ruta_dir}/{tabla}_limpio.json"
    # Convierte nulos de pandas a None para JSON/Mongo
    datos = df.astype(object).where(pd.notna(df), None).to_dict("records")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    logger.info("Guardados %d registros en %s", len(datos), ruta)

def cargar_mongo() -> None:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as exc:
        logger.error("MongoDB no disponible en %s (%s). Ejecuta antes: docker compose up -d", MONGO_URI, exc)
        return

    db = client[DB]
    for tabla in TABLAS:
        docs = []
        for anyo in sorted(os.listdir(DIR_SALIDA)):
            ruta = f"{DIR_SALIDA}/{anyo}/{tabla}_limpio.json"
            if os.path.isfile(ruta):
                with open(ruta, encoding="utf-8") as f:
                    docs.extend(json.load(f))
        db[tabla].drop()
        if docs:
            db[tabla].insert_many(docs)
    logger.info("Carga en MongoDB (%s) completada", DB)
    client.close()

if __name__ == "__main__":
    for anyo in sorted(os.listdir(DIR_RAW)):
        carpeta = os.path.join(DIR_RAW, anyo)
        if not os.path.isdir(carpeta):
            continue
        for tabla in TABLAS:
            rutas = ultimas_rutas_raw(carpeta, tabla)
            if not rutas:
                logger.warning("%s/%s: no hay fichero raw", anyo, tabla)
                continue
            with open(rutas[-1], encoding="utf-8") as f:  # el mas reciente
                df = limpiar(pd.DataFrame(json.load(f)), tabla)
            guardar(df, anyo, tabla)

    cargar_mongo()
