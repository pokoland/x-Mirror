from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from bot import download_dict, application, download_dict_lock, DOWNLOAD_DIR
from bot.helper.ext_utils.fs_utils import clean_download
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage

from time import sleep
from bot.helper.ext_utils.bot_utils import getDownloadByGid, MirrorStatus, getAllDownload


async def cancel_mirror(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split(" ", maxsplit=1)
    mirror_message = None
    keys = []
    if len(args) > 1:
        gid = args[1]
        dl = getDownloadByGid(gid)
        if not dl:
            await sendMessage(f"GID : <code>{gid}</code> Introuvable.", context.bot, update)
            return
        mirror_message = dl.message
    elif update.message.reply_to_message:
        mirror_message = update.message.reply_to_message
        with download_dict_lock:
            keys = list(download_dict.keys())
            try:
                dl = download_dict[mirror_message.message_id]
            except:
                dl = None

    if len(args) == 1:
        msg = f"Veuillez répondre au message <code>/{BotCommands.MirrorCommand}</code> qui a été utilisé pour démarrer le téléchargement ou envoyer <code>/{BotCommands.CancelMirror} GID</code> pour l'annuler !"
        if mirror_message and mirror_message.message_id not in keys:
            if BotCommands.MirrorCommand in mirror_message.text or \
               BotCommands.TarMirrorCommand in mirror_message.text or \
               BotCommands.UnzipMirrorCommand in mirror_message.text:
                msg1 = "Le mirroring a déjà été annulé"
                await sendMessage(msg1, context.bot, update)
            else:
                await sendMessage(msg, context.bot, update)
            return
        elif not mirror_message:
            await sendMessage(msg, context.bot, update)
            return

    if dl is None:
        await sendMessage("Téléchargement introuvable.", context.bot, update)
        return

    if dl.status() == MirrorStatus.STATUS_ARCHIVING:
        await sendMessage("Archivage en cours, vous ne pouvez pas l'annuler.", context.bot, update)
    elif dl.status() == MirrorStatus.STATUS_EXTRACTING:
        await sendMessage("Extraction en cours, vous ne pouvez pas l'annuler.", context.bot, update)
    elif dl.status() == MirrorStatus.STATUS_SPLITTING:
        await sendMessage("Découpage en cours, vous ne pouvez pas l'annuler.", context.bot, update)
    else:
        dl.download().cancel_download()
        sleep(3)  # au cas où ondownloaderror listener échoue
        clean_download(f'{DOWNLOAD_DIR}{mirror_message.message_id}')
        await sendMessage("Téléchargement annulé et nettoyé.", context.bot, update)


async def cancel_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = 0
    gid = 0
    while True:
        dl = getAllDownload()
        if dl:
            if dl.gid() != gid:
                gid = dl.gid()
                dl.download().cancel_download()
                count += 1
                sleep(0.3)
        else:
            break
    await sendMessage(f'{count} téléchargement(s) ont été annulés !', context.bot, update)


application.add_handler(CommandHandler(
    BotCommands.CancelMirror,
    cancel_mirror,
    filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user) & CustomFilters.mirror_owner_filter | CustomFilters.sudo_user
))

application.add_handler(CommandHandler(
    BotCommands.CancelAllCommand,
    cancel_all,
    filters=CustomFilters.owner_filter | CustomFilters.sudo_user
))
