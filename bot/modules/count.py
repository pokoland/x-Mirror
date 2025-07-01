# Implémenté par - @anasty17 (https://github.com/SlamDevs/slam-mirrorbot/pull/111)
# (c) https://github.com/SlamDevs/slam-mirrorbot
# Tous droits réservés

from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import deleteMessage, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import application


async def countNode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        msg = await sendMessage(f"Comptage : <code>{link}</code>", context.bot, update)
        gd = GoogleDriveHelper()
        result = gd.count(link)
        await deleteMessage(context.bot, msg)

        uname = f'@{update.message.from_user.username}' if update.message.from_user.username else f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        cc = f'\n\n<b>cc : </b>{uname}'

        await sendMessage(result + cc, context.bot, update)
    else:
        await sendMessage("Veuillez fournir un lien partageable Google Drive à compter.", context.bot, update)


application.add_handler(CommandHandler(
    BotCommands.CountCommand,
    countNode,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user
))
