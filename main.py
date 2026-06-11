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


def _input_opcion(prompt, opciones, error_msg=None):
    opciones = tuple(opciones)
    while True:
        opcion = input(prompt).strip().upper()
        if opcion in opciones:
            return opcion
        print(error_msg or f"Opción inválida. Elija: {' o '.join(opciones)}")


def _seleccionar_raza():
    import string
    lista = list(RAZAS.keys())
    letras = string.ascii_uppercase[:len(lista)]
    for letra, raza in zip(letras, lista):
        print(f"{letra}. {raza.capitalize()}")
    opcion = _input_opcion("\nElije una raza: ", letras, f"Opción inválida. Elija una letra entre la {letras[0]} a la {letras[-1]}")
    return lista[letras.index(opcion)]


def _seleccionar_sexo():
    print("\n1. Masculino (M)")
    print("2. Femenino (F)")
    while True:
        opcion = input("\nElije el sexo: ").strip().upper()
        if opcion in ("1", "M"):
            return "masculino"
        if opcion in ("2", "F"):
            return "femenino"
        print("Opción inválida. Elija 1/M o 2/F.")


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
    guardar = input("\n¿Desea guardar los nombres? (S/N): ").strip().upper()
    if guardar != "S":
        print("\nNo se guardaron los nombres.")
        return
    nombre_archivo = input("Nombre del archivo: ").strip()
    if not nombre_archivo:
        print("\nNombre inválido. No se guardó nada.")
        return
    guardar_nombres(nombres, f"{nombre_archivo}.txt")
    print(f"\nArchivo '{nombre_archivo}.txt' guardado correctamente.\n")


def main():
    limpiar()
    print("=== NameForge RPG ===\n")

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

        opcion = input("\n¿Quieres salir de la aplicación? (S/N): ").strip().upper()
        if opcion == "S":
            print("\n¡Gracias por usar NameForge RPG! Que tus aventuras sean legendarias!")
            break


if __name__ == "__main__":
    main()
