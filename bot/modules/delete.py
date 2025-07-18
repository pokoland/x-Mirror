import asyncio
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot import application, LOGGER
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.upload_utils import gdriveTools


async def deletefile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_args = update.message.text.split(' ', maxsplit=1)
    reply_to = update.message.reply_to_message

    if len(msg_args) > 1:
        link = msg_args[1]
    elif reply_to is not None:
        reply_text = reply_to.text
        link = reply_text.split('\n')[0]
    else:
        link = None

    if link is not None:
        LOGGER.info(link)
        drive = gdriveTools.GoogleDriveHelper()
        msg = drive.deletefile(link)
        LOGGER.info(f"Résultat de la suppression : {msg}")
    else:
        msg = 'Veuillez envoyer le lien Gdrive avec la commande ou en y répondant.'

    reply_message = await sendMessage(msg, context.bot, update)
    asyncio.create_task(auto_delete_message(context.bot, update.message, reply_message))


application.add_handler(CommandHandler(
    BotCommands.DeleteCommand,
    deletefile,
    filters=CustomFilters.owner_filter | CustomFilters.sudo_user
))
