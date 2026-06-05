
import json
import os
import subprocess

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_razas():
    path = os.path.join(_BASE_DIR, "races.json")
    with open(path, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_nombres(nombres, nombre_archivo):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for nombre in nombres:
            archivo.write(nombre + "\n")


def limpiar_pantalla():
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)