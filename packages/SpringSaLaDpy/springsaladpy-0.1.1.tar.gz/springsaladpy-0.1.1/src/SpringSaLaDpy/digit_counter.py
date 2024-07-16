from decimal import Decimal, getcontext

def count_digits(number, precision):
    getcontext().prec = precision
    decimal_number = Decimal(str(number))
    decimal_places = -decimal_number.as_tuple().exponent

    return decimal_places