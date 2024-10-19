from aiogram import Bot, Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.requests import (
    del_contractor,
    delete_additionally,
    delete_category,
    delete_product,
    delete_region,
    delete_series,
    delete_ticket,
    get_ticket,
)
from app.filters.chat_types import ChatTypeFilter


delete = Router()

delete.message.filter(ChatTypeFilter(["private"]))

########


@delete.callback_query(F.data.startswith("new-ticket-delete_"))
async def delete_new_ticket(
    callback: types.CallbackQuery, bot: Bot, session: AsyncSession
):
    ticket_id = callback.data.split("_")[-1]
    ticket = await get_ticket(ticket_id)
    await callback.answer()
    try:
        await bot.send_message(
            chat_id=ticket.tg_id,
            text=f"❌ Ваша заявка №{ticket.id} на продукт {ticket.product} была удалена!",
        )
        await delete_ticket(session, ticket_id)
    except Exception as e:
        await callback.message.answer("❌ Неудача")
        await callback.message.answer(f"Ошибка {e}, попробуйте ещё раз!")


########


@delete.callback_query(F.data.startswith("delete-additionally_"))
async def delete_additionaly_handler(
    callback: types.CallbackQuery, session: AsyncSession
):
    add_id = callback.data.split("_")[-1]
    await callback.answer()
    try:
        await delete_additionally(session, add_id)
        await callback.message.answer("Успех ✅")
        await callback.message.answer(f"Доп. опция удалена!")
    except Exception as e:
        await callback.message.answer("❌ Неудача")
        await callback.message.answer(f"Ошибка {e}, попробуйте ещё раз!")


########


@delete.callback_query(F.data.startswith("delete-region_"))
async def delete_region_handler(callback: types.CallbackQuery, session: AsyncSession):
    reg_id = callback.data.split("_")[-1]
    await callback.answer()
    try:
        await delete_region(session, reg_id)
        await callback.message.answer("Успех ✅")
        await callback.message.answer("Регион удален!")
    except Exception as e:
        await callback.message.answer("❌ Неудача")
        await callback.message.answer(f"Ошибка {e}, попробуйте ещё раз!")


########


@delete.callback_query(F.data.startswith("delete-category_"))
async def delete_category_handler(callback: types.CallbackQuery, session: AsyncSession):
    cat_id = callback.data.split("_")[-1]
    await callback.answer()
    try:
        await delete_category(session, cat_id)
        await callback.message.answer("Успех ✅")
        await callback.message.answer(f"Категория удалена!")
    except Exception as e:
        await callback.message.answer("❌ Неудача")
        await callback.message.answer(f"Ошибка {e}, попробуйте ещё раз!")


########


@delete.callback_query(F.data.startswith("delete-series_"))
async def delete_series_handler(callback: types.CallbackQuery, session: AsyncSession):
    series_id = callback.data.split("_")[-1]
    await callback.answer()
    try:
        await delete_series(session, series_id)
        await callback.message.answer("Успех ✅")
        await callback.message.answer(f"Серия удалена!")
    except Exception as e:
        await callback.message.answer("❌ Неудача")
        await callback.message.answer(f"Ошибка {e}, попробуйте ещё раз!")


########


@delete.callback_query(F.data.startswith("delete-product_"))
async def delete_product_handler(callback: types.CallbackQuery, session: AsyncSession):
    prodict_id = callback.data.split("_")[-1]
    await callback.answer()
    try:
        await delete_product(session, prodict_id)
        await callback.message.answer("Успех ✅")
        await callback.message.answer(f"Продукт удалён!")
    except Exception as e:
        await callback.message.answer("❌ Неудача")
        await callback.message.answer(f"Ошибка {e}, попробуйте ещё раз!")


########


@delete.callback_query(F.data.startswith("delete-contractor_"))
async def delete_contractor_handler(callback: types.CallbackQuery, session: AsyncSession):
    contractor_id = callback.data.split("_")[-1]
    await callback.answer()
    try:
        await del_contractor(contractor_id)
        await callback.message.answer("Успех ✅")
        await callback.message.answer(f"Продукт удалён!")
    except Exception as e:
        await callback.message.answer("❌ Неудача")
        await callback.message.answer(f"Ошибка {e}, попробуйте ещё раз!")


########
