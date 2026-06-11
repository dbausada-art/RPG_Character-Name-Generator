from utils import cargar_razas, guardar_nombres, limpiar
from generador import generar_nombre
import translations

RAZAS = cargar_razas()


def _input_int(prompt, min_val=None):
    while True:
        try:
            valor = int(input(prompt))
            if min_val is not None and valor < min_val:
                print(translations.T["min_value"].format(val=min_val))
                continue
            return valor
        except ValueError:
            print(translations.T["invalid_int"])


def _input_opcion(prompt, opciones, error_msg=None):
    opciones = tuple(opciones)
    while True:
        opcion = input(prompt).strip().upper()
        if opcion in opciones:
            return opcion
        print(error_msg or translations.T["invalid_option"].format(
            opts=translations.T["or_connector"].join(opciones)
        ))


def _seleccionar_raza():
    import string
    lista = list(RAZAS.keys())
    letras = string.ascii_uppercase[:len(lista)]
    for letra, raza in zip(letras, lista):
        nombre_raza = translations.T["races"].get(raza, raza.capitalize())
        print(f"{letra}. {nombre_raza}")
    opcion = _input_opcion(
        translations.T["choose_race"],
        letras,
        translations.T["invalid_race"].format(first=letras[0], last=letras[-1]),
    )
    return lista[letras.index(opcion)]


def _seleccionar_sexo():
    print(f"\n1. {translations.T['masculine']}")
    print(f"2. {translations.T['feminine']}")
    while True:
        opcion = input(translations.T["choose_gender"]).strip().upper()
        if opcion in ("1", "M"):
            return "masculino"
        if opcion in ("2", "F"):
            return "femenino"
        print(translations.T["invalid_gender"])


def _pedir_configuracion():
    cantidad = _input_int(translations.T["how_many"], min_val=1)
    min_silabas = _input_int(translations.T["min_syllables"], min_val=2)
    max_silabas = _input_int(translations.T["max_syllables"])
    if max_silabas < min_silabas:
        max_silabas = min_silabas
    return cantidad, min_silabas, max_silabas


def _generar_nombres(datos, cantidad, min_silabas, max_silabas):
    max_combinaciones = (
        len(datos["inicio"]) * len(datos["medio"]) * len(datos["final"])
    )
    if cantidad > max_combinaciones:
        print(translations.T["limit_adjusted"].format(max=max_combinaciones))
        cantidad = max_combinaciones
    nombres = set()
    while len(nombres) < cantidad:
        nombres.add(generar_nombre(datos, min_silabas, max_silabas))
    return nombres


def _manejar_guardado(nombres):
    guardar = input(translations.T["save_prompt"]).strip().upper()
    if guardar != translations.T["save_yes"]:
        print(translations.T["not_saved"])
        return
    nombre_archivo = input(translations.T["filename_prompt"]).strip()
    if not nombre_archivo:
        print(translations.T["invalid_filename"])
        return
    guardar_nombres(nombres, f"{nombre_archivo}.txt")
    print(translations.T["saved_ok"].format(file=nombre_archivo))


def _seleccionar_idioma():
    while True:
        opcion = input(
            "Seleccione un idioma / Select a language:\n"
            "1. Español\n"
            "2. English\n"
            "> "
        ).strip()
        if opcion in ("1", "2"):
            translations.set_lang(opcion)
            return
        print("Opción inválida. Elija 1 o 2. / Invalid option. Choose 1 or 2.")


def main():
    limpiar()
    print("=== NameForge RPG ===\n")
    _seleccionar_idioma()
    limpiar()
    print(translations.T["title"] + "\n")

    while True:
        raza = _seleccionar_raza()
        sexo = _seleccionar_sexo()
        datos = RAZAS.get(raza, {}).get(sexo)
        if not datos:
            print(translations.T["no_data"].format(race=raza, gender=sexo))
            continue

        cantidad, min_silabas, max_silabas = _pedir_configuracion()
        nombres = _generar_nombres(datos, cantidad, min_silabas, max_silabas)

        print(translations.T["generated_header"])
        for nombre in sorted(nombres):
            print(nombre)

        _manejar_guardado(nombres)

        opcion = input(translations.T["exit_prompt"]).strip().upper()
        if opcion == translations.T["exit_yes"]:
            print(translations.T["goodbye"])
            break


if __name__ == "__main__":
    main()
