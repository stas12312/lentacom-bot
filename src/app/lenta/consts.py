import enum


class SkuStock:
    NONE = "None"
    FEW = "Few"
    ENOUGH = "Enough"
    MANY = "Many"


SKU_STOCK_TRANSLATE = {
    SkuStock.NONE: "Нет товара",
    SkuStock.FEW: "Товар заканчивается",
    SkuStock.ENOUGH: "Товара достаточно",
    SkuStock.MANY: "Товара много",
}

SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
