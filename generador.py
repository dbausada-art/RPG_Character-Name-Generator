import random


def generar_nombre(
    datos,
    min_silabas,
    max_silabas
):

    cantidad_silabas = random.randint(
        min_silabas,
        max_silabas
    )

    nombre = random.choice(
        datos["inicio"]
    )

    for _ in range(cantidad_silabas - 2):
        nombre += random.choice(
            datos["medio"]
        )

    nombre += random.choice(
        datos["final"]
    )

    return nombre