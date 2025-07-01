import os
import asyncio
from PIL import Image

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from bot import AS_DOC_USERS, AS_MEDIA_USERS, AS_DOCUMENT, app, AUTO_DELETE_MESSAGE_DURATION, application
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, auto_delete_message
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper import button_build


async def leechSet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    path = f"Thumbnails/{user_id}.jpg"
    msg = f"Type de leech pour l'utilisateur {user_id} : "
    if user_id in AS_DOC_USERS or (user_id not in AS_MEDIA_USERS and AS_DOCUMENT):
        msg += "DOCUMENT"
    else:
        msg += "MEDIA"

    msg += "\nMiniature personnalisée "
    msg += "existe" if os.path.exists(path) else "n'existe pas"

    buttons = button_build.ButtonMaker()
    buttons.sbutton("En tant que Document", f"doc {user_id}")
    buttons.sbutton("En tant que Media", f"med {user_id}")
    buttons.sbutton("Supprimer la miniature", f"thumb {user_id}")
    if AUTO_DELETE_MESSAGE_DURATION == -1:
        buttons.sbutton("Fermer", f"closeset {user_id}")

    button = InlineKeyboardMarkup(buttons.build_menu(2))
    choose_msg = await sendMarkup(msg, context.bot, update, button)
    asyncio.create_task(auto_delete_message(context.bot, update.message, choose_msg))


async def setLeechType(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split(" ")

    if user_id != int(data[1]):
        await query.answer(text="Ce n'est pas à vous !", show_alert=True)
        return

    if data[0] == "doc":
        if user_id in AS_DOC_USERS or (user_id not in AS_MEDIA_USERS and AS_DOCUMENT):
            await query.answer(text="Déjà en tant que Document !", show_alert=True)
        else:
            AS_MEDIA_USERS.discard(user_id)
            AS_DOC_USERS.add(user_id)
            await query.answer(text="Fait !", show_alert=True)

    elif data[0] == "med":
        if user_id in AS_DOC_USERS:
            AS_DOC_USERS.remove(user_id)
            AS_MEDIA_USERS.add(user_id)
            await query.answer(text="Fait !", show_alert=True)
        elif user_id in AS_MEDIA_USERS or not AS_DOCUMENT:
            await query.answer(text="Déjà en tant que Media !", show_alert=True)
        else:
            AS_MEDIA_USERS.add(user_id)
            await query.answer(text="Fait !", show_alert=True)

    elif data[0] == "thumb":
        path = f"Thumbnails/{user_id}.jpg"
        if os.path.lexists(path):
            os.remove(path)
            await query.answer(text="Fait !", show_alert=True)
        else:
            await query.answer(text="Aucune miniature à supprimer !", show_alert=True)

    elif data[0] == "closeset":
        await query.message.delete()


async def setThumb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    reply_to = update.message.reply_to_message

    if reply_to and reply_to.photo:
        path = "Thumbnails/"
        os.makedirs(path, exist_ok=True)

        photo_msg = await app.get_messages(update.message.chat.id, reply_to.message_id)
        photo_dir = await app.download_media(photo_msg, file_name=path)

        des_dir = os.path.join(path, f"{user_id}.jpg")
        img = Image.open(photo_dir)
        img.thumbnail((480, 320))
        img.save(des_dir, "JPEG")
        os.remove(photo_dir)

        await sendMessage(f"Miniature personnalisée enregistrée pour l'utilisateur <code>{user_id}</code>.", context.bot, update)
    else:
        await sendMessage("Répondez à une photo pour enregistrer une miniature personnalisée.", context.bot, update)


application.add_handler(CommandHandler(
    BotCommands.LeechSetCommand, leechSet,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user))

application.add_handler(CommandHandler(
    BotCommands.SetThumbCommand, setThumb,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user))

application.add_handler(CallbackQueryHandler(setLeechType, pattern="^doc "))
application.add_handler(CallbackQueryHandler(setLeechType, pattern="^med "))
application.add_handler(CallbackQueryHandler(setLeechType, pattern="^thumb "))
application.add_handler(CallbackQueryHandler(setLeechType, pattern="^closeset "))
