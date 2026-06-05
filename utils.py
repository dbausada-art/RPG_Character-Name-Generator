import json
import os


def cargar_razas():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "races.json")
    try:
        with open(path, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{path}'.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: el archivo JSON no es válido: {e}")
        raise


def guardar_nombres(nombres, nombre_archivo):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            for nombre in sorted(nombres):
                archivo.write(nombre + "\n")
    except OSError as e:
        print(f"Error al guardar el archivo '{nombre_archivo}': {e}")
        raise


def limpiar():
    os.system("cls" if os.name == "nt" else "clear")
