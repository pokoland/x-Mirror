from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot import LOGGER, application
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands


async def list_drive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        search = update.message.text.split(' ', maxsplit=1)[1]
        LOGGER.info(f"Recherche : {search}")

        reply = await sendMessage('Recherche en cours... Veuillez patienter !', context.bot, update)

        gdrive = GoogleDriveHelper()
        msg, button = gdrive.drive_list(search)

        if button:
            await editMessage(msg, reply, button)
        else:
            await editMessage(f"Aucun résultat trouvé pour <i>{search}</i>", reply)

    except IndexError:
        await sendMessage('Veuillez envoyer un mot-clé de recherche avec la commande.', context.bot, update)


application.add_handler(CommandHandler(
    BotCommands.ListCommand,
    list_drive,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user
))
