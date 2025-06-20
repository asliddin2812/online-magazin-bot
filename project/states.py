from aiogram.fsm.state import StatesGroup, State

class RegisterStates(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    address = State()

class CategoryStates(StatesGroup):
    add_category = State()
    delete_category = State()

class ProductStates(StatesGroup):
    add_product_name = State()
    add_product_category = State()
    add_product_price = State()
    add_product_description = State()
    search_product = State()
    delete_product = State()
    update_product_id = State()
    update_product_field = State()
    update_product_value = State()