import snooker_colors as cr
points = {
    "pink": 6,
    "blue": 5,
    "green": 3,
    "yellow": 2,
    "brown": 4,
    "black": 7,
    "white": 4
}

def get_potted_color(map):
    result = []
    if map.get(cr.PINK) is None:
        result.append(cr.PINK)
    if map.get(cr.BLUE) is None:
        result.append(cr.BLUE)
    """if map.get(cr.GREEN) is None:
        result.append(cr.GREEN)"""
    if map.get(cr.YELLOW) is None:
        result.append(cr.YELLOW)
    if map.get(cr.BROWN) is None:
        result.append(cr.BROWN)
    if map.get(cr.WHITE) is None:
        result.append(cr.WHITE)
    if map.get(cr.BLACK) is None:
        result.append(cr.BLACK)
    return result


#pot buffers for balls
red_buffer = 0
pink_buffer = 0
blue_buffer = 0
green_buffer = 0
yellow_buffer = 0
brown_buffer = 0
black_buffer = 0
white_buffer = 0


def pot_confirm():
    if pink_buffer == 200:
        return "pink"
    if blue_buffer == 30:
        return "blue"
    if green_buffer == 200:
        return "green"
    if yellow_buffer == 200:
        return "yellow"
    if brown_buffer == 250:
        return "brown"
    if black_buffer == 200:
        return "brown"
    if white_buffer == 200:
        return "white"
    return "none"
