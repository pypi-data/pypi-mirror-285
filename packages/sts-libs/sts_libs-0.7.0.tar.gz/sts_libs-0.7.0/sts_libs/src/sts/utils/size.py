"""size.py: Module to convert human size <=> bytes."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import re

size_human_regex = re.compile(r'([\-0-9\.]+)(Ki|Mi|Gi|Ti|Ei|Zi){0,1}B$')


def size_human_check(size_human):  # noqa: ANN001, ANN201
    size_human = str(size_human)
    m = size_human_regex.match(size_human)
    if not m:
        logging.error(f'size_human_check() - incorrect number format {size_human}')
        return False
    return True


def size_human_2_size_bytes(size_human):  # noqa: ANN001, ANN201
    """Usage
        size_human_2_size_bytes(size_human)
    Purpose
        Convert human readable stander size to B
    Parameter
        size_human     # like '1KiB'
    Returns
        size_bytes     # like 1024.
    """
    if not size_human:
        return None

    # make sure size_human is a string, could be only numbers, for example
    size_human = str(size_human)
    if not re.search(r'\d', size_human):
        # Need at least 1 digit
        return None

    m = size_human_regex.match(size_human)
    if not m:
        if re.match(r'^\d+$', size_human):
            # Assume size is already in bytes
            return size_human
        logging.error(f"'{size_human}' is an invalid human size format")
        return None

    fraction = 0
    # check if number is fractional
    f = re.match(r'(\d+)\.(\d+)', m.group(1))
    if f:
        number = int(f.group(1))
        fraction = int(f.group(2))
    else:
        number = int(m.group(1))

    unit = m.group(2)
    if not unit:
        unit = 'B'

    for valid_unit in ('B', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi'):
        if unit == valid_unit:
            if unit == 'B':
                # cut any fraction if was given, as it is not valid
                return str(number)
            return int(number + fraction)
        number *= 1024
        fraction *= 1024
        fraction /= 10
    return int(number + fraction)


def size_bytes_2_size_human(num):  # noqa: ANN001, ANN201
    if not num:
        return None

    # Even if we receive string we , so we can process it
    num = int(num)
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB'):
        if abs(num) < 1024.0:
            size_human = f'{num:3.1f}{unit}'
            # round it down removing decimal numbers
            return re.sub(r'\.\d+', '', size_human)
        num /= 1024.0
    # Very big number!!
    size_human = f'{num:.1f}Yi'
    # round it down removing decimal numbers
    return re.sub(r'\.\d+', '', size_human)
