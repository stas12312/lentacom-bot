from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class City(BaseModel):
    id: str
    name: str
    lat: float
    long: float
    medium_store_conceration: bool = Field(alias="mediumStoreConcentration")
    high_store_concetration: bool = Field(alias="highStoreConcentration")
    delivery_option_popup_default_value: Optional[str] = Field(alias="deliveryOptionPopupDefaultValue")


class Store(BaseModel):
    id: str
    name: str
    address: str
    city_key: str = Field(alias="cityKey")
    city_name: str = Field(alias="cityName")
    type: str
    lat: float
    long: float
    opens_at: Optional[int] = Field(alias="opensAt")
    closes_at: Optional[int] = Field(alias="closesAt")
    is_default_store: bool = Field(alias="isDefaultStore")
    is_ecom_available: bool = Field(alias="isEcomAvailable")
    is_pickup_available: bool = Field(alias="isPickupAvailable")
    is_delivery_available: bool = Field(alias="isDeliveryAvailable")
    is_24_h_store: bool = Field(alias="is24hStore")
    has_pet_shop: bool = Field(alias="hasPetShop")
    division: str
    is_favorite: bool = Field(alias="isFavorite")
    min_order_summ: Optional[int] = Field(alias="minOrderSumm")
    max_order_summ: Optional[int] = Field(alias="maxOrderSumm")
    min_delivery_order_summ: Optional[int] = Field(alias="minDeliveryOrderSumm")
    max_delivery_order_summ: Optional[int] = Field(alias="maxDeliveryOrderSumm")
    max_weight: Optional[int] = Field(alias="maxWeight")
    max_delivery_weight: Optional[int] = Field(alias="maxDeliveryWeight")
    max_quantity_per_item: Optional[int] = Field(alias="maxQuantityPerItem")
    max_delivery_quantity_per_item: Optional[int] = Field(alias="maxDeliveryQuantityPerItem")
    order_limit_overall: Optional[int] = Field(alias="orderLimitOverall")
    delivery_order_livit_overall: Optional[int] = Field(alias="deliveryOrderLimitOverall")
    store_timezone_offset: str = Field(alias="storeTimeZoneOffset")


class Image(BaseModel):
    thumbnail: HttpUrl
    medium: HttpUrl
    full_size: HttpUrl = Field(alias="fullSize")
    meduim_lossy: HttpUrl = Field(alias="mediumLossy")


class BaseCategory(BaseModel):
    code: str
    name: str


class DetailCategory(BaseCategory):
    sku_count: int = Field(alias="skuCount")
    sku_discounts_count: int = Field(alias="skuDiscountCount")
    show_lentochka_banner: bool = Field(alias="showLentochkaBanner")
    image: Optional[Image]
    url: str


class ChildCategory(DetailCategory):
    pass


class Category(DetailCategory):
    subcategories: list[ChildCategory]


class RootCategory(DetailCategory):
    categories: list[Category]


class LentochkaPromotion(BaseModel):
    banner: Optional[str]
    banner_url: Optional[str] = Field(alias="bannerUrl")


class Catalog(BaseModel):
    catalog_groups: list[RootCategory] = Field(alias="catalogGroups")
    lentochka_promotion: LentochkaPromotion = Field(alias="lentochkaPromotion")


class Categories(BaseModel):
    group: BaseCategory
    category: BaseCategory
    subcategory: BaseCategory


class BaseSku(BaseModel):
    promo_id: Optional[str] = Field(alias="promoId")
    price_by_promocode: Optional[float] = Field(alias="priceByProcomode")
    code: str
    title: str
    brand: Optional[str]
    sub_title: str = Field(alias="subTitle")
    descitpion: Optional[str]
    regular_price: float = Field(alias="regularPrice")
    discount_price: Optional[float] = Field(alias="discountPrice")
    offer_descitpion: Optional[str] = Field(alias="offerDescription")
    promo_type: Optional[str] = Field(alias="promoType")
    validity_start_date: Optional[datetime] = Field(alias="validityStartDate")
    validity_end_date: Optional[datetime] = Field(alias="validityEndDate")
    image: Optional[Image] = None
    images: list[Image]
    stamps_price: Optional[str] = Field(alias="stampsPrice")
    web_url: HttpUrl = Field(alias="webUrl")
    order_limit: Optional[int] = Field(alias="orderLimit")
    order_steps: Optional[list[float]] = Field(alias="orderSteps")
    sku_weight: float = Field(alias="skuWeight")
    is_available_for_order: bool = Field(alias="isAvailableForOrder")
    is_available_for_delivery: bool = Field(alias="isAvailableForDelivery")
    is_weight_product: bool = Field(alias="isWeightProduct")
    stock: str
    categories: Categories


class CommonSku(BaseSku):
    place_output: str = Field(alias="placeOutput")
    comments_count: int = Field(alias="commentsCount")
    average_rating: float = Field(alias="averageRating")

    promo_precent: int = Field(alias="promoPercent")
