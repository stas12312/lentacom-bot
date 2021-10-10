from lenta.client import LentaClient
from lenta.models import BaseSku


async def search_sku_in_store(store_id: str, sku_name: str, lenta_client: LentaClient) -> list[BaseSku]:
    """Получение товаров по совпадению в названии"""
    return await lenta_client.search_skus_in_store(store_id, sku_name)
