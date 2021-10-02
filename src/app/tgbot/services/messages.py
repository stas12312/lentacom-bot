from typing import Optional

import aiogram.utils.markdown as md

from lenta.models import Store, BaseSku
from lenta.utils import translate_sku_stock, parse_weight_from_barcode


def get_store_info_message(store: Store) -> str:
    """
    Формирование текста для информации о магазине
    :param store: Магазин
    :return: Текстовая информация о магазине
    """
    return md.text("🏢 Город:", md.escape_md(store.city_name), "\n",
                   "📍 Адрес:", md.escape_md(store.address), "\n",
                   "🕓 Время работы:", md.text(store.opens_at), md.escape_md("-"), md.text(store.closes_at),
                   sep="")


def get_sku_info_message(sku: BaseSku, barcode: Optional[str] = None) -> str:
    """
    Формирование текста для информации о товаре
    :param sku: Товар
    :param barcode: Значение штрих-кода
    :return: Текстовая информация о товаре
    """
    discount = round(sku.regular_price - sku.discount_price, 2) if sku.discount_price else None
    stock = translate_sku_stock(sku.stock)
    msg_parts = []
    price = sku.discount_price if sku.discount_price else sku.regular_price
    postfix_price = "кг." if sku.is_weight_product else "шт."
    price_str = md.text(md.escape_md(sku.discount_price), md.strikethrough(sku.regular_price)) \
        if sku.discount_price else sku.regular_price

    if barcode:
        msg_parts.append(md.escape_md("🎹 Штрих-код:", md.bold(barcode)))

    msg_parts.extend([
        md.text("ℹ️ Товар:", md.escape_md(sku.title)),
        md.text("🔄 Количество:", stock),
    ])

    if sku.is_weight_product and barcode:
        weight = parse_weight_from_barcode(barcode)
        price_on_kg = round(weight * price, 2)
        price_msg_part = md.text("💵 Цена:", md.escape_md(price_on_kg), "за", md.escape_md(weight, "кг."))

    else:
        price_msg_part = md.text("💵 Цена:", price_str, "за", md.escape_md(postfix_price))
    msg_parts.append(price_msg_part)

    if discount:
        msg_parts.extend([
            md.text("🎁 Скидка:", md.escape_md(discount))
        ])

    return md.text(*msg_parts, sep="\n")


def get_sku_list_message(skus: list[BaseSku]) -> str:
    """Формирование сообщения для списка товаров"""
    msg_parts = ["🗒 Список добавленных товаров"]
    msg_parts.extend([get_sku_info_message(sku) for sku in skus])

    return md.text(*msg_parts, sep="\n\n")
