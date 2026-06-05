
import json
import subprocess

def cargar_razas():
    with open("races.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_nombres(nombres, nombre_archivo):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for nombre in nombres:
            archivo.write(nombre + "\n")


def limpiar_pantalla():

    subprocess.run("cls", shell=True)