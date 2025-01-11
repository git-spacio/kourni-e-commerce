
import re
from itertools import cycle


def format_rut(rut):
    # Eliminar todos los puntos y guiones
    cleaned_rut = re.sub(r'[.-]', '', rut)

    # Agregar los puntos y el guion en los lugares correctos
    # formatted_rut = f'{cleaned_rut[:-8]}.{cleaned_rut[-8:-5]}.{cleaned_rut[-5:-1]}-{cleaned_rut[-1]}'
    formatted_rut = f'{cleaned_rut[:-7]}.{cleaned_rut[-7:-4]}.{cleaned_rut[-4:-1]}-{cleaned_rut[-1]}'
    return formatted_rut


def check_rut(rut):
    # Extracción de número y dígito verificador
    rut_number = rut[:-2].replace(".", "")
    dv = rut[-1].upper()

    reversed_digits = map(int, reversed(str(rut_number)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    check_digit = (-s) % 11

    if check_digit == 10:
        check_digit = 'K'

    return str(check_digit) == dv