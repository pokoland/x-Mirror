import time
import psutil
import shutil
import asyncio

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot import status_reply_dict, status_reply_dict_lock, download_dict, download_dict_lock, botStartTime, application
from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage, sendStatusMessage, auto_delete_message
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands


async def mirror_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with download_dict_lock:
        if len(download_dict) == 0:
            currentTime = get_readable_time(time.time() - botStartTime)
            total, used, free = shutil.disk_usage('.')
            free = get_readable_file_size(free)

            message = 'Aucun téléchargement actif !\n___________________________\n'
            message += (
                f"<b>CPU :</b> {psutil.cpu_percent()}%"
                f" <b>DISQUE :</b> {psutil.disk_usage('/').percent}%"
                f" <b>RAM :</b> {psutil.virtual_memory().percent}%"
                f"\n<b>LIBRE :</b> {free} | <b>UPTIME :</b> {currentTime}"
            )

            reply_message = await sendMessage(message, context.bot, update)
            asyncio.create_task(auto_delete_message(context.bot, update.message, reply_message))
            return

    index = update.effective_chat.id
    async with status_reply_dict_lock:
        if index in status_reply_dict.keys():
            await deleteMessage(context.bot, status_reply_dict[index])
            del status_reply_dict[index]

    await sendStatusMessage(update, context.bot)
    await deleteMessage(context.bot, update.message)


application.add_handler(CommandHandler(
    BotCommands.StatusCommand,
    mirror_status,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user
))
