from aiogram.utils.callback_data import CallbackData

city_cb = CallbackData("city", "city_id")
store_cb = CallbackData("store", "store_id")

add_sku_cb = CallbackData("add_sku", "sku_code")
delete_sku_cb = CallbackData("delete_sku", "sku_code")

choice_group = CallbackData("c_group_category", "group_code")
choice_category = CallbackData("c_category", "category_code")
choice_subcategory = CallbackData("c_subcategory", "subcategory_code")
