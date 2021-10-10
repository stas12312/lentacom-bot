def distance_between_points(x1: float, y1: float, x2: float, y2: float) -> float:
    """Вычисление расстояния между двумя точками"""

    x_dist = x2 - x1
    y_dist = y2 - y1

    return ((x_dist ** 2) + (y_dist ** 2)) ** 0.5
