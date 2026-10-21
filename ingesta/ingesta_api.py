
import os
import json
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/8414A/"
API_KEY = os.getenv("AEMET_API_KEY")

def obtener_datos(pagina: int = 1, tamanio: int = 100) -> list[dict]:
    """Obtiene los datos meteorológicos de la API."""
    params = {"api_key": API_KEY}
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()

    respuesta = resp.json()

    if "datos" not in respuesta:
        raise ValueError(f"AEMET no devolvió la URL de descarga: {respuesta}")

    url_datos = respuesta["datos"]

    descarga = requests.get(url_datos, timeout=30)
    descarga.raise_for_status()

    return descarga.json()

def ingesta_completa() -> list[dict]:
    """Obtiene todos los registros devueltos por AEMET."""
    registros = obtener_datos()
    return registros

if __name__ == "__main__":
    registros = ingesta_completa()
    fecha = date.today().isoformat()
    ruta_salida = f"data/raw/dataset_{fecha}.json"
    os.makedirs("data/raw", exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    print(f"Ingesta completada: {len(registros)} registros guardados en {ruta_salida}")
