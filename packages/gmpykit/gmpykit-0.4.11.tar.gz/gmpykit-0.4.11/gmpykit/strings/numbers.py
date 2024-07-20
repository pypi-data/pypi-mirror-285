
def percent(nb: float) -> str:
    """Format the number sent into a % number, eg 0.012 into "01.2%" """
    the_number = round(100 * nb, 2)
    the_string = "{: >6.2f}%".format(the_number)
    return the_string


def readable_number(number:float) -> str:
    """Convert the given number into a more readable string"""

    for x in ['', 'k', 'M', 'B']:
        if number < 1000.0: return str(round(number, 1)) + x
        number /= 1000.0
    raise Exception("This Exception should never happen")


def readable_bytes(bytes_nb: float) -> str:
    """Convert bytes to KB, or MB or GB"""

    for x in ["B", "kB", "MB", "GB", "TB"]:
        if bytes_nb < 1000.0: return "%3.1f %s" % (bytes_nb, x)
        bytes_nb /= 1000.0
    raise Exception("This Exception should never happen")


def readable_time(seconds: int) -> str:
    """Convert second number into Minutes, Hours, Days, ..."""

    if seconds < 60: return f'{seconds}sec'

    minutes = seconds / 60
    if minutes < 60: return f'{round(minutes, 1)}min'

    hours = minutes / 60
    if hours < 24: return f'{round(hours, 1)}h'

    days = hours / 24
    if days < 30.4: return f'{round(days, 1)}h'

    months = days / 30.4
    if months < 12: return f'{round(months, 1)}months'

    years = months / 12
    return f'{round(years, 1)}years'

