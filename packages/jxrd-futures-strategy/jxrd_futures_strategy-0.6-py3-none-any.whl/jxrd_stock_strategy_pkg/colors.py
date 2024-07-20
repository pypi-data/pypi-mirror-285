colors = {
    'blue': 255,
    'brown': 10053120,
    'gray': 10066329,
    'green': 65280,
    'purple': 10027263,
    'red': 16711680,
    'yellow': 16776960
}


def rgb_red():
    return colors.get('red')


def rgb_brown():
    return colors.get('brown')


def rgb_gray():
    return colors.get('gray')


def rgb_green():
    return colors.get('green')


def rgb_purple():
    return colors.get('purple')


def rgb_yellow():
    return colors.get('yellow')


def rgb_to_hex_without_hash(rgb):
    return '0x{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
