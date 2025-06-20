from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import db
from project.states import CategoryStates, ProductStates

shop_router = Router()

def get_menu(data: str):
    menus = {
        "main": [
            ["📋 Kategoriyalar", "categories"],
            ["➕ Mahsulot qo'shish", "add_product"],
            ["🔍 Qidirish", "search_product"],
            ["🗑 O'chirish", "delete_product"],
            ["✏️ O'zgartirish", "update_product"],
            ["📦 Mahsulotlar", "list_products"]
        ],
        "categories": [
            ["➕ Qo'shish", "add_category"],
            ["📋 Ko'rish", "list_categories"],
            ["🗑 O'chirish", "delete_category"],
            ["⬅️ Ortga", "back_to_main"]
        ],
        "update": [
            ["Nomi", "update_name"],
            ["Kategoriyasi", "update_category"],
            ["Narxi", "update_price"],
            ["Tavsifi", "update_description"],
            ["⬅️ Ortga", "back_to_main"]
        ]
    }
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=c)] for t, c in menus[data]])

async def handle_error(message: Message, error_msg: str):
    await message.answer(f"❌ {error_msg}")

@shop_router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Amalni tanlang:", reply_markup=get_menu("main"))
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "categories")
async def categories_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Kategoriyalar:", reply_markup=get_menu("categories"))
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "add_category")
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Kategoriya nomini kiriting:")
    await state.set_state(CategoryStates.add_category)
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "list_categories")
async def list_categories(callback: CallbackQuery):
    categories = db.get_categories()
    msg = "📋 Kategoriyalar:\n" + "\n".join([f"ID: {c[0]} - {c[1]}" for c in categories]) if categories else "Kategoriya mavjud emas."
    await callback.message.answer(msg, reply_markup=get_menu("categories"))
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "delete_category")
async def delete_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Kategoriya ID sini kiriting:")
    await state.set_state(CategoryStates.delete_category)
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "add_product")
async def add_product(callback: CallbackQuery, state: FSMContext):
    if not db.get_categories():
        await callback.message.answer("❌ Avval kategoriya qo'shing!", reply_markup=get_menu("main"))
    else:
        await callback.message.answer("Mahsulot nomini kiriting:")
        await state.set_state(ProductStates.add_product_name)
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "search_product")
async def search_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Mahsulot nomini kiriting:")
    await state.set_state(ProductStates.search_product)
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "delete_product")
async def delete_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Mahsulot ID sini kiriting:")
    await state.set_state(ProductStates.delete_product)
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "update_product")
async def update_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Mahsulot ID sini kiriting:")
    await state.set_state(ProductStates.update_product_id)
    await callback.answer()

@shop_router.callback_query(lambda c: c.data == "list_products")
async def list_products(callback: CallbackQuery):
    products = db.search_products("")
    msg = "📦 Mahsulotlar:\n" + "\n".join([f"ID: {p[0]}\nNomi: {p[1]}\nKategoriya: {p[2]}\nNarxi: {p[3]} UZS\nTavsif: {p[4]}" for p in products]) if products else "Mahsulot mavjud emas."
    await callback.message.answer(msg, reply_markup=get_menu("main"))
    await callback.answer()

@shop_router.message(CategoryStates.add_category)
async def process_add_category(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await handle_error(message, "Nom bo'sh bo'lmasligi kerak!")
    elif db.add_category(name):
        await message.answer(f"✅ '{name}' qo'shildi!", reply_markup=get_menu("categories"))
    else:
        await handle_error(message, "Bu nom allaqachon mavjud!")
    await state.clear()

@shop_router.message(CategoryStates.delete_category)
async def process_delete_category(message: Message, state: FSMContext):
    try:
        cat_id = int(message.text)
        if any(p[2] == cat_id for p in db.search_products("")):
            await handle_error(message, "Kategoriyada mahsulotlar bor!")
        elif db.delete_category(cat_id):
            await message.answer("✅ O'chirildi!", reply_markup=get_menu("categories"))
        else:
            await handle_error(message, "Bunday ID topilmadi!")
    except ValueError:
        await handle_error(message, "ID raqam bo'lishi kerak!")
    await state.clear()

@shop_router.message(ProductStates.add_product_name)
async def process_product_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await handle_error(message, "Nom bo'sh bo'lmasligi kerak!")
        return
    await state.update_data(product_name=name)
    cats = db.get_categories()
    msg = "📋 Kategoriya tanlang:\n" + "\n".join([f"ID: {c[0]} - {c[1]}" for c in cats])
    await message.answer(msg)
    await state.set_state(ProductStates.add_product_category)

@shop_router.message(ProductStates.add_product_category)
async def process_product_category(message: Message, state: FSMContext):
    try:
        cat_id = int(message.text)
        if any(c[0] == cat_id for c in db.get_categories()):
            await state.update_data(category_id=cat_id)
            await message.answer("Narxni kiriting:")
            await state.set_state(ProductStates.add_product_price)
        else:
            await handle_error(message, "Bunday kategoriya topilmadi!")
    except ValueError:
        await handle_error(message, "ID raqam bo'lishi kerak!")

@shop_router.message(ProductStates.add_product_price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            await handle_error(message, "Narx 0 dan katta bo'lishi kerak!")
        else:
            await state.update_data(price=price)
            await message.answer("Tavsifni kiriting:")
            await state.set_state(ProductStates.add_product_description)
    except ValueError:
        await handle_error(message, "Narx raqam bo'lishi kerak!")

@shop_router.message(ProductStates.add_product_description)
async def process_product_description(message: Message, state: FSMContext):
    desc = message.text.strip()
    data = await state.get_data()
    if not desc:
        await handle_error(message, "Tavsif bo'sh bo'lmasligi kerak!")
    elif db.add_product(data['product_name'], data['category_id'], data['price'], desc):
        await message.answer("✅ Qo'shildi!", reply_markup=get_menu("main"))
    else:
        await handle_error(message, "Xatolik yuz berdi!")
    await state.clear()

@shop_router.message(ProductStates.search_product)
async def process_search_product(message: Message, state: FSMContext):
    query = message.text.strip()
    products = db.search_products(query)
    msg = "🔍 Topilganlar:\n" + "\n".join([f"ID: {p[0]}\nNomi: {p[1]}\nKategoriya: {p[2]}\nNarxi: {p[3]} UZS\nTavsif: {p[4]}" for p in products]) if products else "❌ Topilmadi!"
    await message.answer(msg, reply_markup=get_menu("main"))
    await state.clear()

@shop_router.message(ProductStates.delete_product)
async def process_delete_product(message: Message, state: FSMContext):
    try:
        prod_id = int(message.text)
        if db.delete_product(prod_id):
            await message.answer("✅ O'chirildi!", reply_markup=get_menu("main"))
        else:
            await handle_error(message, "Bunday ID topilmadi!")
    except ValueError:
        await handle_error(message, "ID raqam bo'lishi kerak!")
    await state.clear()

@shop_router.message(ProductStates.update_product_id)
async def process_update_product_id(message: Message, state: FSMContext):
    try:
        prod_id = int(message.text)
        if any(p[0] == prod_id for p in db.search_products("")):
            await state.update_data(product_id=prod_id)
            await message.answer("Maydonni tanlang:", reply_markup=get_menu("update"))
            await state.set_state(ProductStates.update_product_field)
        else:
            await handle_error(message, "Bunday ID topilmadi!")
    except ValueError:
        await handle_error(message, "ID raqam bo'lishi kerak!")

@shop_router.callback_query(lambda c: c.data.startswith("update_"))
async def process_update_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.replace("update_", "")
    await state.update_data(update_field=field)
    await callback.message.answer(f"Yangi {field} ni kiriting:")
    await state.set_state(ProductStates.update_product_value)
    await callback.answer()

@shop_router.message(ProductStates.update_product_value)
async def process_update_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field, prod_id = data['update_field'], data['product_id']
    value = message.text.strip()
    if not value:
        await handle_error(message, f"{field} bo'sh bo'lmasligi kerak!")
        return
    if field == "category":
        try:
            value = int(value)
            if not any(c[0] == value for c in db.get_categories()):
                await handle_error(message, "Bunday kategoriya topilmadi!")
                return
        except ValueError:
            await handle_error(message, "ID raqam bo'lishi kerak!")
            return
    elif field == "price":
        try:
            value = float(value)
            if value <= 0:
                await handle_error(message, "Narx 0 dan katta bo'lishi kerak!")
                return
        except ValueError:
            await handle_error(message, "Narx raqam bo'lishi kerak!")
            return
    if db.update_product(prod_id, **{field: value}):
        await message.answer(f"✅ {field} o'zgartirildi!", reply_markup=get_menu("main"))
    else:
        await handle_error(message, "Xatolik yuz berdi!")
    await state.clear()
