import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from sys import executable

from telegram.constants import ParseMode
from telegram.ext import CommandHandler
from telegraph import Telegraph
from wserver import start_server_async
from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, PORT, alive, web, nox, OWNER_ID, AUTHORIZED_CHATS, telegraph_token
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, delete, speedtest, count, leech_settings, search


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>Durée de fonctionnement du bot :</b> <code>{currentTime}</code>\n' \
            f'<b>Espace disque total :</b> <code>{total}</code>\n' \
            f'<b>Utilisé :</b> <code>{used}</code>' \
            f'<b>Libre :</b> <code>{free}</code>\n\n' \
            f'<b>Upload :</b> <code>{sent}</code>\n' \
            f'<b>Download :</b> <code>{recv}</code>\n\n' \
            f'<b>CPU :</b> <code>{cpuUsage}%</code>' \
            f'<b>RAM :</b> <code>{memory}%</code>' \
            f'<b>DISQUE :</b> <code>{disk}%</code>'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://www.github.com/anasty17/mirror-leech-telegram-bot")
    buttons.buildbutton("Groupe", "https://t.me/mirrorLeechTelegramBot")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
Ce bot peut copier tous vos liens vers Google Drive !
Tapez /{BotCommands.HelpCommand} pour obtenir la liste des commandes disponibles
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup('Utilisateur non autorisé', context.bot, update, reply_markup)

def restart(update, context):
    restart_message = sendMessage("Redémarrage en cours...", context.bot, update)
    # Sauvegarder le message de redémarrage pour y répondre après
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.kill()
    process = psutil.Process(web.pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
    nox.kill()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Début du ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b> : Obtenir ce message d'aide
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [lien_de_téléchargement][lien_magnet] : Commencer à copier le lien vers Google Drive
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [lien_de_téléchargement][lien_magnet] : Copier et compresser (.zip) le téléchargement
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [lien_de_téléchargement][lien_magnet] : Copier et extraire les archives vers Google Drive
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [lien_magnet] : Copier en utilisant qBittorrent, utilisez <b>/{BotCommands.QbMirrorCommand} s</b> pour sélectionner les fichiers
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [lien_magnet] : Copier en utilisant qBittorrent et compresser (.zip)
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [lien_magnet] : Copier en utilisant qBittorrent et extraire les archives
<br><br>
<b>/{BotCommands.LeechCommand}</b> [lien_de_téléchargement][lien_magnet] : Télécharger vers Telegram, utilisez <b>/{BotCommands.LeechCommand} s</b> pour sélectionner les fichiers
<br><br>
<b>/{BotCommands.ZipLeechCommand}</b> [lien_de_téléchargement][lien_magnet] : Télécharger vers Telegram sous forme compressée (.zip)
<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b> [lien_de_téléchargement][lien_magnet] : Télécharger vers Telegram et extraire les archives
<br><br>
<b>/{BotCommands.QbLeechCommand}</b> [lien_magnet] : Télécharger vers Telegram en utilisant qBittorrent
<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b> [lien_magnet] : Télécharger vers Telegram en utilisant qBittorrent sous forme compressée (.zip)
<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b> [lien_magnet] : Télécharger vers Telegram en utilisant qBittorrent et extraire les archives
<br><br>
<b>/{BotCommands.CloneCommand}</b> [lien_drive] : Copier un fichier/dossier vers Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [lien_drive] : Compter les fichiers/dossiers d'un lien Google Drive
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [lien_drive] : Supprimer un fichier de Google Drive (Propriétaire & Sudo uniquement)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [lien_youtube-dl] : Copier via youtube-dl. Tapez <b>/{BotCommands.WatchCommand}</b> pour plus d'aide
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [lien_youtube-dl] : Copier via youtube-dl et compresser avant envoi
<br><br>
<b>/{BotCommands.LeechWatchCommand}</b> [lien_youtube-dl] : Télécharger via youtube-dl vers Telegram
<br><br>
<b>/{BotCommands.LeechZipWatchCommand}</b> [lien_youtube-dl] : Télécharger via youtube-dl vers Telegram sous forme compressée
<br><br>
<b>/{BotCommands.LeechSetCommand}</b> : Paramètres de téléchargement
<br><br>
<b>/{BotCommands.SetThumbCommand}</b> : Répondre à une photo pour la définir comme miniature
<br><br>
<b>/{BotCommands.CancelMirror}</b> : Répondre au message de téléchargement pour l'annuler
<br><br>
<b>/{BotCommands.CancelAllCommand}</b> : Annuler toutes les tâches en cours
<br><br>
<b>/{BotCommands.ListCommand}</b> [requête] : Rechercher dans Google Drive
<br><br>
<b>/{BotCommands.SearchCommand}</b> [requête] : Rechercher des torrents avec les plugins de qbittorrent
<br><br>
<b>/{BotCommands.StatusCommand}</b> : Afficher l'état des téléchargements
<br><br>
<b>/{BotCommands.StatsCommand}</b> : Afficher les statistiques de la machine
'''
help = Telegraph(access_token=telegraph_token).create_page(
        title='Aide Mirrorbot',
        author_name='Mirrorbot',
        author_url='https://github.com/anasty17/mirror-leech-telegram-bot',
        html_content=help_string_telegraph,
    )["path"]

help_string = f'''
/{BotCommands.PingCommand} : Vérifier le temps de réponse du bot

/{BotCommands.AuthorizeCommand} : Autoriser un chat ou un utilisateur (Propriétaire & Sudo uniquement)

/{BotCommands.UnAuthorizeCommand} : Révoquer l'accès d'un chat ou utilisateur (Propriétaire & Sudo uniquement)

/{BotCommands.AuthorizedUsersCommand} : Afficher les utilisateurs autorisés (Propriétaire & Sudo uniquement)

/{BotCommands.AddSudoCommand} : Ajouter un utilisateur sudo (Propriétaire uniquement)

/{BotCommands.RmSudoCommand} : Retirer un utilisateur sudo (Propriétaire uniquement)

/{BotCommands.RestartCommand} : Redémarrer le bot

/{BotCommands.LogCommand} : Obtenir les logs du bot (Propriétaire & Sudo uniquement)

/{BotCommands.SpeedCommand} : Tester la vitesse de la connexion

/{BotCommands.ShellCommand} : Exécuter des commandes shell (Propriétaire uniquement)

/{BotCommands.ExecHelpCommand} : Aide pour le module Executor (Propriétaire uniquement)
'''

def bot_help(update, context):
    button = button_build.ButtonMaker()
    button.buildbutton("Autres commandes", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

def main():
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(PORT))
    # Vérifier si le bot redémarre
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Redémarré avec succès !", chat_id, msg_id)
        os.remove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot redémarré !</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)
    start_handler = CommandHandler(BotCommands.StartCommand, start)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.run_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot démarré !")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()