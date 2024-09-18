from aiogram import F, Bot, types, Router
from aiogram.types import InputMediaPhoto, InputMediaDocument
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.requests import add_finished_documents, delete_ticket, get_ticket, get_tickets_by_region, update_ticket_status
from app.filters.chat_types import ChatTypeFilter
from app.keyboards import inline
from common.texts.group import group_id


user_group = Router()


user_group.message.filter(ChatTypeFilter(["group", "supergroup"]))
user_group.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))


async def get_tickets(message, bot, status):
    
    if status == "Новая":
        btns={
        "Показать вложения" : f"ticket-media_{ticket.id}",
        "Принять в работу" : f"new-ticket-to-progress_{ticket.id}",
        "Удалить" : f"new-ticket-delete_{ticket.id}",
        }
    elif status == "В работе":
        btns={
        "Показать вложения" : f"ticket-media_{ticket.id}",
        "Завершить" : f"progress-ticket-to-finished_{ticket.id}",
        }
    
    chat_id = str(message.chat.id)
    key_found = None
    for key, value in group_id.items():
        if value == chat_id:
            key_found = key
            break
    if key_found is not None:
        all_tickets = await get_tickets_by_region(key_found)
        for ticket in all_tickets:
            if ticket.status == status:
                await bot.send_message(chat_id=int(chat_id), 
text=f"Заявка <strong>№{ticket.id}</strong>\n\
Статус: <strong>{ticket.status}</strong>\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: <strong>{ticket.series}</strong>\n\
Комлпектация: {ticket.equipment}\n\
Доп. информация: <strong>{ticket.additionally}</strong>\n\
Комментарий: {ticket.not_exist}",
    reply_markup=inline.get_callback_btns(btns=btns,
    sizes=(1,)
    )
)
    else:
        await bot.send_message(chat_id=chat_id,
                               text="В данный момент нет новых заявок\n\n\
Выберите или введите команду /progress, для проосмотра заявок в работе")
        

async def get_one_new_ticket(callback, ticket_id):
    ticket = await get_ticket(ticket_id)
    btns={
        "Показать вложения" : f"ticket-media_{ticket.id}",
        "Принять в работу" : f"new-ticket-to-progress_{ticket.id}",
        "Удалить" : f"new-ticket-delete_{ticket.id}",
        }
    await callback.message.edit_text(f"Заявка <strong>№{ticket.id}</strong>\n\
Статус: <strong>{ticket.status}</strong>\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: <strong>{ticket.series}</strong>\n\
Комлпектация: {ticket.equipment}\n\
Доп. информация: <strong>{ticket.additionally}</strong>\n\
Комментарий: {ticket.not_exist}",
    reply_markup=inline.get_callback_btns(btns=btns,
    sizes=(1,)
    )
)

##################################### Статус заявок ###############################################
@user_group.message(Command("new"))
async def new_tickets_from_command(message: types.Message, bot: Bot):
    await get_tickets(message, bot, status="Новая")
    
@user_group.callback_query(F.data.startswith("new-ticket_"))
async def new_tickets_from_callback(callback: types.CallbackQuery, bot: Bot):
    await callback.answer()
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)
    await get_one_new_ticket(callback=callback, ticket_id=ticket_id)
    
@user_group.message(Command("progress"))
async def progress_tickets_from_command(message: types.Message, bot: Bot):
    await get_tickets(message, bot, status="В работе")
    
@user_group.callback_query(F.data==("progress_tickets"))
async def new_tickets_from_callback(callback: types.CallbackQuery, bot: Bot):
    await callback.answer()
    await get_tickets(callback.message, bot, status="В работе")    
  
################################## Вложение к заявке ##############################################
@user_group.callback_query(F.data.startswith("ticket-media_"))
async def get_tickets_media(callback: types.CallbackQuery, bot: Bot):
    
    await callback.answer()
    
    chat_id = callback.message.chat.id
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)
    
    photos = ticket.images
    documents = ticket.documents

    # Разделяем строки с ID на отдельные элементы, если строки не пустые
    photo_ids = photos.split(", ") if photos else []
    document_ids = documents.split(", ") if documents else []

    # Создаем список медиа объектов для отправки
    media_photos = []
    media_documents = []
    # Добавляем фото в медиа группу
    for photo_id in photo_ids:
        media_photos.append(InputMediaPhoto(media=photo_id))
    # Добавляем документы в медиа группу
    for doc_id in document_ids:
        media_documents.append(InputMediaDocument(media=doc_id))
    # Проверяем, есть ли медиа для отправки
    if media_photos:
        # Отправляем медиа группу
        await bot.send_media_group(chat_id=chat_id, media=media_photos)
        await bot.send_message(chat_id, f"Фотографии к заявке №{ticket.id}")
    if media_documents:
        # Отправляем медиа группу
        await bot.send_media_group(chat_id=chat_id, media=media_documents)
        await bot.send_message(chat_id, f"Документы к заявке №{ticket.id}")
    if not media_photos:
        # Если нет фото, отправляем уведомление
        await bot.send_message(chat_id, f"Нет фото для отправки по заявке №{ticket.id}")
    if not media_documents:
        # Если нет документов, отправляем уведомление
        await bot.send_message(chat_id, f"Нет документов для отправки по заявке №{ticket.id}")
    if not media_documents and not media_photos:
        # Если нет медиа, отправляем уведомление
        await bot.send_message(chat_id, f"Нет медиа для отправки по заявке №{ticket.id}")
        
###################################################################################################

#################################### Принятие в работу ############################################
@user_group.callback_query(F.data.startswith("new-ticket-to-progress_"))
async def to_progress_new_ticket(callback: types.CallbackQuery, bot: Bot, session: AsyncSession):
    await callback.answer()
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)
    await update_ticket_status(session, ticket_id, "В работе")
    await bot.send_message(chat_id=ticket.tg_id, text=f"Ваша заявка №{ticket_id}\
 на продукт <strong>{ticket.product}</strong> взята в работу, ожидайте!")
    await callback.message.edit_text(f"Заявка №{ticket_id} взята в работу")

###################################################################################################

#################################### Удаление заявки ##############################################
@user_group.callback_query(F.data.startswith("new-ticket-delete_"))
async def delete_new_ticket(callback: types.CallbackQuery, bot: Bot, session: AsyncSession):
    await callback.answer()
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)
    await delete_ticket(session, ticket_id)
    await callback.message.edit_text(f"Заявка №{ticket_id} удалена")
    await bot.send_message(chat_id=group_id[ticket.region], text=f"Заявка №{ticket_id} удалена")
    
