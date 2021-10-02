from .consts import SKU_STOCK_TRANSLATE


def translate_sku_stock(en_stock: str) -> str:
    """
    Перевод информации о количестве товара
    :param en_stock: Исходная информация о товаре
    :return: Переведенная строка
    """

    return SKU_STOCK_TRANSLATE.get(en_stock, "")


def parse_weight_from_barcode(barcode: str) -> float:
    """
    Получение веса товара из штрих-кода
    :param barcode: Штрих-код
    :return: Вес товара в кг.
    """
    raw_weight = barcode[-4:-1]
    weight = float(raw_weight) / 1000
    return round(weight, 3)
