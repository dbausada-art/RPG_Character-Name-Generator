
from utils import (
    cargar_razas,
    guardar_nombres,
    limpiar_pantalla
)
from generador import generar_nombre


def main():

    while True:

        razas = cargar_razas()

        limpiar_pantalla()
        print("=== GENERADOR DE NOMBRES RPG ===")
        print("\nSeleccione una raza para comenzar:\n")

        lista_razas = list(razas.keys())

        for indice, raza in enumerate(lista_razas, start=1):
            print(f"{indice}. {raza.capitalize()}")

        opcion_raza = int(
            input("\nSeleccione una raza: ")
        )

        raza = lista_razas[opcion_raza - 1]

        print("\n1. Masculino")
        print("2. Femenino")

        opcion_sexo = input(
            "\nSeleccione sexo: "
        )

        sexo = (
            "masculino"
            if opcion_sexo == "1"
            else "femenino"
        )

        cantidad = int(
            input(
                "\n¿Cuántos nombres desea generar? "
            )
        )

        min_silabas = int(
            input(
                "\nCantidad mínima de sílabas (mínimo 2): "
            )
        )

        if min_silabas < 2:
            min_silabas = 2

        max_silabas = int(
            input(
                "Cantidad máxima de sílabas: "
            )
        )

        if max_silabas < min_silabas:
            max_silabas = min_silabas

        datos = razas[raza][sexo]

        nombres = set()

        while len(nombres) < cantidad:
            nombres.add(
                generar_nombre(
                    datos,
                    min_silabas,
                    max_silabas
                )
            )

        print("\n=== NOMBRES GENERADOS ===\n")

        for nombre in sorted(nombres):
            print(nombre)

        guardar = input(
            "\n¿Desea guardar los nombres? (s/n): "
        ).lower()

        if guardar == "s":

            nombre_archivo = input(
                "Nombre del archivo: "
            )

            guardar_nombres(
                nombres,
                f"{nombre_archivo}.txt"
            )

            print(
                f"\nArchivo '{nombre_archivo}.txt' guardado correctamente."
            )

        else:
            print(
                "\nNo se guardaron los nombres."
            )

        opcion = input(
            "\nPresione 1 para volver al menú o cualquier otra tecla para salir: "
        )

        if opcion != "1":
            print("\n¡Hasta luego!")
            break


if __name__ == "__main__":
    main()