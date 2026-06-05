from utils import cargar_razas, guardar_nombres, limpiar
from generador import generar_nombre

RAZAS = cargar_razas()


def _input_int(prompt, min_val=None):
    while True:
        try:
            valor = int(input(prompt))
            if min_val is not None and valor < min_val:
                print(f"El valor mínimo es {min_val}.")
                continue
            return valor
        except ValueError:
            print("Entrada inválida. Ingrese un número entero.")


def _input_opcion(prompt, opciones):
    while True:
        opcion = input(prompt).strip()
        if opcion in opciones:
            return opcion
        print(f"Opción inválida. Elija: {', '.join(sorted(opciones))}")


def _seleccionar_raza():
    print("\nSeleccione una raza para comenzar:\n")
    lista = list(RAZAS.keys())
    for i, raza in enumerate(lista, start=1):
        print(f"{i}. {raza.capitalize()}")
    idx = _input_int("\nSeleccione una raza: ", min_val=1)
    while idx > len(lista):
        print(f"Opción inválida. Elija entre 1 y {len(lista)}.")
        idx = _input_int("\nSeleccione una raza: ", min_val=1)
    return lista[idx - 1]


def _seleccionar_sexo():
    print("\n1. Masculino")
    print("2. Femenino")
    opcion = _input_opcion("\nSeleccione sexo (Masculino/Femenino): ", {"1", "2"})
    return "masculino" if opcion == "1" else "femenino"


def _pedir_configuracion():
    cantidad = _input_int("\n¿Cuántos nombres desea generar? ", min_val=1)
    min_silabas = _input_int("\nMínimo de sílabas (mín 2): ", min_val=2)
    max_silabas = _input_int("Máximo de sílabas: ")
    if max_silabas < min_silabas:
        max_silabas = min_silabas
    return cantidad, min_silabas, max_silabas


def _generar_nombres(datos, cantidad, min_silabas, max_silabas):
    max_combinaciones = (
        len(datos["inicio"]) * len(datos["medio"]) * len(datos["final"])
    )
    if cantidad > max_combinaciones:
        print(f"Límite: {max_combinaciones} nombres. Ajustando cantidad.")
        cantidad = max_combinaciones
    nombres = set()
    while len(nombres) < cantidad:
        nombres.add(generar_nombre(datos, min_silabas, max_silabas))
    return nombres


def _manejar_guardado(nombres):
    guardar = input("\n¿Desea guardar los nombres? (s/n): ").strip().lower()
    if guardar != "s":
        print("\nNo se guardaron los nombres.")
        return
    nombre_archivo = input("Nombre del archivo: ").strip()
    if not nombre_archivo:
        print("\nNombre inválido. No se guardó nada.")
        return
    guardar_nombres(nombres, f"{nombre_archivo}.txt")
    print(f"\nArchivo '{nombre_archivo}.txt' guardado correctamente.")


def main():
    limpiar()
    print("=== GENERADOR DE NOMBRES RPG ===\n")

    while True:
        raza = _seleccionar_raza()
        sexo = _seleccionar_sexo()
        datos = RAZAS.get(raza, {}).get(sexo)
        if not datos:
            print(f"\nError: no hay datos para {raza}/{sexo}.")
            continue

        cantidad, min_silabas, max_silabas = _pedir_configuracion()
        nombres = _generar_nombres(datos, cantidad, min_silabas, max_silabas)

        print("\n=== NOMBRES GENERADOS ===\n")
        for nombre in sorted(nombres):
            print(nombre)

        _manejar_guardado(nombres)

        opcion = input(
            "\nPresione 1 para menú o cualquier tecla para salir: "
        ).strip()
        if opcion != "1":
            print("\n¡Hasta luego!")
            break


if __name__ == "__main__":
    main()
