"""Indicador del dashboard: número de suspensos por módulo en la 1.ª evaluación.

Pipeline (las mismas etapas que se prueban en mongosh):
  1. $match  -> Evaluacion "01" (1.ª evaluación) y Nota < 5.
                Nota es un string en la colección, por eso se convierte con $toInt.
  2. $group  -> agrupa por Modulo contando cuántos suspensos hay.
  3. $sort   -> ordena de mayor a menor número de suspensos.
"""

from pymongo import MongoClient

URI = "mongodb://admin:admin@localhost:27018/?authSource=admin"

PIPELINE = [
    {
        "$match": {
            "Evaluacion": "01",
            "$expr": {"$lt": [{"$toInt": "$Nota"}, 5]},
        },
    },
    {"$group": {"_id": "$Modulo", "suspensos": {"$sum": 1}}},
    {"$sort": {"suspensos": -1}},
]


def main():
    cliente = MongoClient(URI)
    coleccion = cliente["mibase"]["calificaciones"]

    print("Suspensos por módulo (1.ª evaluación):")
    for doc in coleccion.aggregate(PIPELINE):
        print(f"  {doc['_id']:<12} {doc['suspensos']}")

    cliente.close()


if __name__ == "__main__":
    main()
