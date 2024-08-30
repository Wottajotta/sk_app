from aiogram import F, Bot, types, Router
from aiogram.types import InputMediaPhoto, InputMediaDocument
from aiogram.filters import Command

from app.db.requests import get_ticket, get_tickets_by_region
from app.filters.chat_types import ChatTypeFilter
from app.keyboards import inline
from common.texts.group import group_id


user_group = Router()

user_group.message.filter(ChatTypeFilter(["group", "supergroup"]))
user_group.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))


async def get_new_tickets(message, bot):
    chat_id = str(message.chat.id)
    key_found = None
    for key, value in group_id.items():
        if value == chat_id:
            key_found = key
            break
    if key_found is not None:
        all_tickets = await get_tickets_by_region(key_found)
        for ticket in all_tickets:
            await bot.send_message(chat_id=int(chat_id), 
text=f"Заявка №{ticket.id}\n\
Статус: {ticket.status}\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: <strong>{ticket.series}</strong>\n\
Доп. информация: <strong>{ticket.additionally}</strong>",
    reply_markup=inline.get_callback_btns(btns={
        "Показать вложения" : f"new-ticket-media_{ticket.id}",
        "Принять в работу" : f"new-ticket-to-progress_{ticket.id}",
        "Удалить" : f"new-ticket-delete_{ticket.id}",
        },
    sizes=(1,)
    )
)
    else:
        await bot.send_message(chat_id=chat_id,text="В данный момент нет новых заявок или произошла ошибка")


@user_group.message(Command("new"))
async def new_tickets_from_command(message: types.Message, bot: Bot):
    await get_new_tickets(message, bot)
    
@user_group.callback_query(F.data==("new_tickets"))
async def new_tickets_from_callback(callback: types.CallbackQuery, bot: Bot):
    await callback.answer()
    await get_new_tickets(callback.message, bot)   
    
@user_group.callback_query(F.data.startswith("new-ticket-media_"))
async def get_new_ticket_media(callback: types.CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)
    
    photos = ticket.images
    documents = ticket.documents

    # Разделяем строки с ID на отдельные элементы, если строки не пустые
    photo_ids = photos.split(", ") if photos else []
    document_ids = documents.split(", ") if documents else []

    # Создаем список медиа объектов для отправки
    media = []

    # Добавляем фото в медиа группу
    for photo_id in photo_ids:
        media.append(InputMediaPhoto(photo_id))

    # Добавляем документы в медиа группу
    for doc_id in document_ids:
        media.append(InputMediaDocument(doc_id))
    
    # Проверяем, есть ли медиа для отправки
    if media:
        # Отправляем медиа группу
        await bot.send_media_group(chat_id, media)
    else:
        # Если нет медиа, отправляем уведомление
        await bot.send_message(chat_id, "Нет медиа для отправки.")