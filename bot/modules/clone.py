import random
import string
from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from bot.helper.mirror_utils.upload_utils import gdriveTools
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, deleteMessage, sendStatusMessage, delete_all_messages, update_all_messages
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import application, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval
from bot.helper.ext_utils.bot_utils import get_readable_file_size


async def cloneNode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    if len(args) > 1:
        link = args[1]
    elif reply_to is not None:
        reply_text = reply_to.text
        link = reply_text.split('\n')[0]
    else:
        link = None

    if link is not None:
        gd = gdriveTools.GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            await sendMessage(res, context.bot, update)
            return

        if STOP_DUPLICATE:
            LOGGER.info('Vérification si le fichier/dossier existe déjà sur Drive...')
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "Le fichier/dossier est déjà disponible sur Drive.\nVoici les résultats de la recherche :"
                await sendMarkup(msg3, context.bot, update, button)
                return

        if CLONE_LIMIT is not None:
            LOGGER.info('Vérification de la taille du fichier/dossier...')
            if size > CLONE_LIMIT * 1024**3:
                msg2 = f'Échec, la limite de clonage est de {CLONE_LIMIT}GB.\nLa taille de votre fichier/dossier est de {get_readable_file_size(size)}.'
                await sendMessage(msg2, context.bot, update)
                return

        if files <= 10:
            msg = await sendMessage(f"Clonage : <code>{link}</code>", context.bot, update)
            result, button = gd.clone(link)
            await deleteMessage(context.bot, msg)
        else:
            drive = gdriveTools.GoogleDriveHelper(name)
            gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
            clone_status = CloneStatus(drive, size, update, gid)
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            await sendStatusMessage(update, context.bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[update.message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    await delete_all_messages()
                else:
                    await update_all_messages()
            except IndexError:
                pass

        uname = f'@{update.message.from_user.username}' if update.message.from_user.username else f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        cc = f'\n\n<b>cc : </b>{uname}'
        men = f'{uname} '

        if button in ["cancelled", ""]:
            await sendMessage(men + result, context.bot, update)
        else:
            await sendMarkup(result + cc, context.bot, update, button)
    else:
        await sendMessage('Veuillez fournir un lien partageable Google Drive à cloner.', context.bot, update)


application.add_handler(CommandHandler(
    BotCommands.CloneCommand,
    cloneNode,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user
))
