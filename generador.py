import random


def generar_nombre(datos, min_silabas, max_silabas):
    for clave in ("inicio", "medio", "final"):
        if clave not in datos or not datos[clave]:
            raise ValueError(f"La lista '{clave}' está vacía o no existe.")

    cantidad_silabas = random.randint(min_silabas, max_silabas)
    nombre = random.choice(datos["inicio"])
    for _ in range(cantidad_silabas - 2):
        nombre += random.choice(datos["medio"])
    nombre += random.choice(datos["final"])
    return nombre
