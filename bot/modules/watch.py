from telegram.ext import CommandHandler
from telegram import Bot, Update
from bot import DOWNLOAD_DIR, dispatcher, LOGGER
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage
from .mirror import MirrorListener
from bot.helper.mirror_utils.download_utils.youtube_dl_download_helper import YoutubeDLHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
import threading


def _watch(bot: Bot, update, isZip=False, isLeech=False):
    mssg = update.message.text
    message_args = mssg.split(' ')
    name_args = mssg.split('|')

    try:
        link = message_args[1]
    except IndexError:
        msg = f"/{BotCommands.WatchCommand} [lien supporté par youtube-dl] [qualité] |[NomPersonnalisé] pour lancer le miroir avec youtube-dl.\n\n"
        msg += "<b>Note : La qualité et le nom personnalisé sont optionnels</b>\n\nExemple de qualité : audio, 144, 240, 360, 480, 720, 1080, 2160."
        msg += "\n\nSi vous souhaitez utiliser un nom de fichier personnalisé, indiquez-le après |"
        msg += f"\n\nExemple :\n/{BotCommands.WatchCommand} https://youtu.be/Pk_TthHfLeE 720 |video.mp4\n\n"
        msg += "Ce fichier sera téléchargé en qualité 720p et son nom sera <b>video.mp4</b>"
        sendMessage(msg, bot, update)
        return

    try:
      if "|" in mssg:
        mssg = mssg.split("|")
        qual = mssg[0].split(" ")[2]
        if qual == "":
          raise IndexError
      else:
        qual = message_args[2]
      if qual != "audio":
        qual = f'bestvideo[height<={qual}]+bestaudio/best[height<={qual}]'
    except IndexError:
      qual = "bestvideo+bestaudio/best"

    try:
      name = name_args[1]
    except IndexError:
      name = ""

    pswd = ""
    listener = MirrorListener(bot, update, pswd, isZip, isLeech=isLeech)
    ydl = YoutubeDLHelper(listener)
    threading.Thread(target=ydl.add_download,args=(link, f'{DOWNLOAD_DIR}{listener.uid}', qual, name)).start()
    sendStatusMessage(update, bot)

def watch(update, context):
    _watch(context.bot, update)

def watchZip(update, context):
    _watch(context.bot, update, True, True)

def leechWatch(update, context):
    _watch(context.bot, update, isLeech=True)

def leechWatchZip(update, context):
    _watch(context.bot, update, True, True, True)

watch_handler = CommandHandler(BotCommands.WatchCommand, watch,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
zip_watch_handler = CommandHandler(BotCommands.ZipWatchCommand, watchZip,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
leech_watch_handler = CommandHandler(BotCommands.LeechWatchCommand, leechWatch,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
leech_zip_watch_handler = CommandHandler(BotCommands.LeechZipWatchCommand, leechWatchZip,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)

dispatcher.add_handler(watch_handler)
dispatcher.add_handler(zip_watch_handler)
dispatcher.add_handler(leech_watch_handler)
dispatcher.add_handler(leech_zip_watch_handler)
