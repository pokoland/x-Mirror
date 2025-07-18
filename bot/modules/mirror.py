from telegram.ext import CommandHandler, Application
from telegram import Update
from bot import Interval, INDEX_URL, BUTTON_FOUR_NAME, BUTTON_FOUR_URL, BUTTON_FIVE_NAME, BUTTON_FIVE_URL, \
                BUTTON_SIX_NAME, BUTTON_SIX_URL, BLOCK_MEGA_FOLDER, BLOCK_MEGA_LINKS, VIEW_LINK, aria2, \
                application, DOWNLOAD_DIR, download_dict, download_dict_lock, SHORTENER, SHORTENER_API, \
                ZIP_UNZIP_LIMIT, TG_SPLIT_SIZE
from bot.helper.ext_utils import fs_utils, bot_utils
from bot.helper.ext_utils.shortenurl import short_url
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException, NotSupportedExtractionArchive
from bot.helper.mirror_utils.download_utils.aria2_download import AriaDownloadHelper
from bot.helper.mirror_utils.download_utils.mega_downloader import MegaDownloadHelper
from bot.helper.mirror_utils.download_utils.qbit_downloader import QbitTorrent
from bot.helper.mirror_utils.download_utils.direct_link_generator import direct_link_generator
from bot.helper.mirror_utils.download_utils.telegram_downloader import TelegramDownloadHelper
from bot.helper.mirror_utils.status_utils import listeners
from bot.helper.mirror_utils.status_utils.extract_status import ExtractStatus
from bot.helper.mirror_utils.status_utils.zip_status import ZipStatus
from bot.helper.mirror_utils.status_utils.split_status import SplitStatus
from bot.helper.mirror_utils.status_utils.upload_status import UploadStatus
from bot.helper.mirror_utils.status_utils.tg_upload_status import TgUploadStatus
from bot.helper.mirror_utils.status_utils.gdownload_status import DownloadStatus
from bot.helper.mirror_utils.upload_utils import gdriveTools, pyrogramEngine
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper import button_build
import urllib.parse
import re
import os
import shutil
import pathlib
import logging
import time
import random
import string
import requests
import subprocess

ariaDlManager = AriaDownloadHelper()
ariaDlManager.start_listener()

LOGGER = logging.getLogger(__name__)

class MirrorListener(listeners.MirrorListeners):
    def __init__(self, update: Update, context, pswd, isZip=False, extract=False, isQbit=False, isLeech=False):
        super().__init__(update, context)
        self.extract = extract
        self.isZip = isZip
        self.isQbit = isQbit
        self.isLeech = isLeech
        self.pswd = pswd

    def onDownloadStarted(self):
        pass

    def onDownloadProgress(self):
        pass

    def clean(self):
        try:
            aria2.purge()
            Interval[0].cancel()
            del Interval[0]
            delete_all_messages()
        except IndexError:
            pass

    def onDownloadComplete(self):
        with download_dict_lock:
            LOGGER.info(f"Téléchargement terminé : {download_dict[self.uid].name()}")
            download = download_dict[self.uid]
            name = str(download.name()).replace('/', '')
            gid = download.gid()
            size = download.size_raw()
            if name == "None" or self.isQbit:
                name = os.listdir(f'{DOWNLOAD_DIR}{self.uid}')[0]
            m_path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        if self.isZip:
            try:
                with download_dict_lock:
                    download_dict[self.uid] = ZipStatus(name, m_path, size)
                pswd = self.pswd
                path = m_path + ".zip"
                LOGGER.info(f'Zip : chemin_origine : {m_path}, chemin_zip : {path}')
                if pswd is not None:
                    subprocess.run(["7z", "a", "-mx=0", f"-p{pswd}", path, m_path])
                else:
                    subprocess.run(["7z", "a", "-mx=0", path, m_path])
            except FileNotFoundError:
                LOGGER.info('Fichier à archiver introuvable !')
                self.onUploadError('Erreur interne !!')
                return
            try:
                shutil.rmtree(m_path)
            except:
                os.remove(m_path)
        elif self.extract:
            try:
                if os.path.isfile(m_path):
                    path = fs_utils.get_base_name(m_path)
                LOGGER.info(f"Extraction : {name}")
                with download_dict_lock:
                    download_dict[self.uid] = ExtractStatus(name, m_path, size)
                pswd = self.pswd
                if os.path.isdir(m_path):
                    for dirpath, subdir, files in os.walk(m_path, topdown=False):
                        for filee in files:
                            if re.search(r'\.part0*1.rar$', filee) or re.search(r'\.7z.0*1$', filee) \
                               or (filee.endswith(".rar") and not re.search(r'\.part\d+.rar$', filee)) \
                               or re.search(r'\.zip.0*1$', filee):
                                m_path = os.path.join(dirpath, filee)
                                if pswd is not None:
                                    result = subprocess.run(["7z", "x", f"-p{pswd}", m_path, f"-o{dirpath}"])
                                else:
                                    result = subprocess.run(["7z", "x", m_path, f"-o{dirpath}"])
                                if result.returncode != 0:
                                    LOGGER.warning('Impossible d\'extraire l\'archive !')
                                break
                        for filee in files:
                            if filee.endswith(".rar") or re.search(r'\.r\d+$', filee) \
                               or re.search(r'\.7z.\d+$', filee) or re.search(r'\.zip.\d+$', filee):
                                del_path = os.path.join(dirpath, filee)
                                os.remove(del_path)
                    path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
                else:
                    if pswd is not None:
                        result = subprocess.run(["pextract", m_path, pswd])
                    else:
                        result = subprocess.run(["extract", m_path])
                    if result.returncode == 0:
                        os.remove(m_path)
                        LOGGER.info(f"Suppression de l'archive : {m_path}")
                    else:
                        LOGGER.warning('Impossible d\'extraire l\'archive ! Envoi quand même')
                        path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
                LOGGER.info(f'Chemin obtenu : {path}')

            except NotSupportedExtractionArchive:
                LOGGER.info("Archive non valide, envoi du fichier tel quel.")
                path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        else:
            path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        up_name = pathlib.PurePath(path).name
        up_path = f'{DOWNLOAD_DIR}{self.uid}/{up_name}'
        size = fs_utils.get_path_size(up_path)
        if self.isLeech:
            checked = False
            for dirpath, subdir, files in os.walk(f'{DOWNLOAD_DIR}{self.uid}', topdown=False):
                for filee in files:
                    f_path = os.path.join(dirpath, filee)
                    f_size = os.path.getsize(f_path)
                    if int(f_size) > TG_SPLIT_SIZE:
                        if not checked:
                            checked = True
                            with download_dict_lock:
                                download_dict[self.uid] = SplitStatus(up_name, up_path, size)
                            LOGGER.info(f"Découpage : {up_name}")
                        fs_utils.split(f_path, f_size, filee, dirpath, TG_SPLIT_SIZE)
                        os.remove(f_path)
            LOGGER.info(f"Nom du Leech : {up_name}")
            tg = pyrogramEngine.TgUploader(up_name, self)
            tg_upload_status = TgUploadStatus(tg, size, gid, self)
            with download_dict_lock:
                download_dict[self.uid] = tg_upload_status
            update_all_messages()
            tg.upload()
        else:
            LOGGER.info(f"Nom de l'envoi : {up_name}")
            drive = gdriveTools.GoogleDriveHelper(up_name, self)
            upload_status = UploadStatus(drive, size, gid, self)
            with download_dict_lock:
                download_dict[self.uid] = upload_status
            update_all_messages()
            drive.upload(up_name)

    def onDownloadError(self, error):
        error = error.replace('<', ' ').replace('>', ' ')
        with download_dict_lock:
            try:
                download = download_dict[self.uid]
                del download_dict[self.uid]
                fs_utils.clean_download(download.path())
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        if self.update.message.from_user.username:
            uname = f"@{self.update.message.from_user.username}"
        else:
            uname = f'<a href="tg://user?id={self.update.message.from_user.id}">{self.update.message.from_user.first_name}</a>'
        msg = f"{uname} votre téléchargement a été arrêté à cause de : {error}"
        sendMessage(msg, self.context.bot, self.update)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

    def onUploadStarted(self):
        pass

    def onUploadProgress(self):
        pass

    def onUploadComplete(self, link: str, size, files, folders, typ):
        if self.isLeech:
            if self.update.message.from_user.username:
                uname = f"@{self.update.message.from_user.username}"
            else:
                uname = f'<a href="tg://user?id={self.update.message.from_user.id}">{self.update.message.from_user.first_name}</a>'
            count = len(files)
            if self.update.message.chat.type == 'private':
                msg = f'<code>{link}</code>\n'
                msg += f'<b>Total des fichiers : </b>{count}'
                if typ != 0:
                    msg += f'\n<b>Fichiers corrompus : </b>{typ}'
                sendMessage(msg, self.context.bot, self.update)
            else:
                chat_id = str(self.update.message.chat.id)[4:]
                msg = f"<a href='https://t.me/c/{chat_id}/{self.uid}'>{link}</a>\n"
                msg += f'<b>Total des fichiers : </b>{count}\n'
                if typ != 0:
                    msg += f'<b>Fichiers corrompus : </b>{typ}\n'
                msg += f'<b>cc : </b>{uname}\n\n'
                fmsg = ''
                for index, item in enumerate(list(files), start=1):
                    msg_id = files[item]
                    link = f"https://t.me/c/{chat_id}/{msg_id}"
                    fmsg += f"{index}. <a href='{link}'>{item}</a>\n"
                    if len(fmsg.encode('utf-8') + msg.encode('utf-8')) > 4000:
                        time.sleep(1.5)
                        sendMessage(msg + fmsg, self.context.bot, self.update)
                        fmsg = ''
                if fmsg != '':
                    time.sleep(1.5)
                    sendMessage(msg + fmsg, self.context.bot, self.update)
            with download_dict_lock:
                try:
                    fs_utils.clean_download(download_dict[self.uid].path())
                except FileNotFoundError:
                    pass
                del download_dict[self.uid]
                count = len(download_dict)
            if count == 0:
                self.clean()
            else:
                update_all_messages()
            return
        with download_dict_lock:
            msg = f'<code>{download_dict[self.uid].name()}</code>\n\n<b>Taille : </b>{size}'
            if os.path.isdir(f'{DOWNLOAD_DIR}/{self.uid}/{download_dict[self.uid].name()}'):
                msg += '\n\n<b>Type : </b>Dossier'
                msg += f'\n<b>Sous-dossiers : </b>{folders}'
                msg += f'\n<b>Fichiers : </b>{files}'
            else:
                msg += f'\n\n<b>Type : </b>{typ}'
            buttons = button_build.ButtonMaker()
            if SHORTENER is not None and SHORTENER_API is not None:
                surl = short_url(link)
                buttons.buildbutton("☁️ Lien Drive", surl)
            else:
                buttons.buildbutton("☁️ Lien Drive", link)
            LOGGER.info(f'Envoi terminé {download_dict[self.uid].name()}')
            if INDEX_URL is not None:
                url_path = requests.utils.quote(f'{download_dict[self.uid].name()}')
                share_url = f'{INDEX_URL}/{url_path}'
                if os.path.isdir(f'{DOWNLOAD_DIR}/{self.uid}/{download_dict[self.uid].name()}'):
                    share_url += '/'
                    if SHORTENER is not None and SHORTENER_API is not None:
                        siurl = short_url(share_url)
                        buttons.buildbutton("⚡ Lien Index", siurl)
                    else:
                        buttons.buildbutton("⚡ Lien Index", share_url)
                else:
                    share_urls = f'{INDEX_URL}/{url_path}?a=view'
                    if SHORTENER is not None and SHORTENER_API is not None:
                        siurl = short_url(share_url)
                        buttons.buildbutton("⚡ Lien Index", siurl)
                        if VIEW_LINK:
                            siurls = short_url(share_urls)
                            buttons.buildbutton("🌐 Lien Vue", siurls)
                    else:
                        buttons.buildbutton("⚡ Lien Index", share_url)
                        if VIEW_LINK:
                            buttons.buildbutton("🌐 Lien Vue", share_urls)
            if BUTTON_FOUR_NAME is not None and BUTTON_FOUR_URL is not None:
                buttons.buildbutton(f"{BUTTON_FOUR_NAME}", f"{BUTTON_FOUR_URL}")
            if BUTTON_FIVE_NAME is not None and BUTTON_FIVE_URL is not None:
                buttons.buildbutton(f"{BUTTON_FIVE_NAME}", f"{BUTTON_FIVE_URL}")
            if BUTTON_SIX_NAME is not None and BUTTON_SIX_URL is not None:
                buttons.buildbutton(f"{BUTTON_SIX_NAME}", f"{BUTTON_SIX_URL}")
            if self.update.message.from_user.username:
                uname = f"@{self.update.message.from_user.username}"
            else:
                uname = f'<a href="tg://user?id={self.update.message.from_user.id}">{self.update.message.from_user.first_name}</a>'
            if uname is not None:
                msg += f'\n\n<b>cc : </b>{uname}'
            try:
                fs_utils.clean_download(download_dict[self.uid].path())
            except FileNotFoundError:
                pass
            del download_dict[self.uid]
            count = len(download_dict)
        sendMarkup(msg, self.context.bot, self.update, buttons.build_menu(2))
        if count == 0:
            self.clean()
        else:
            update_all_messages()

    def onUploadError(self, error):
        e_str = error.replace('<', '').replace('>', '')
        with download_dict_lock:
            try:
                fs_utils.clean_download(download_dict[self.uid].path())
            except FileNotFoundError:
                pass
            del download_dict[self.uid]
            count = len(download_dict)
        if self.update.message.from_user.username:
            uname = f"@{self.update.message.from_user.username}"
        else:
            uname = f'<a href="tg://user?id={self.update.message.from_user.id}">{self.update.message.from_user.first_name}</a>'
        if uname is not None:
            men = f'{uname} '
        sendMessage(men + e_str, self.context.bot, self.update)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

def _mirror(update: Update, context, isZip=False, extract=False, isQbit=False, isLeech=False):
    mesg = update.message.text.split('\n')
    message_args = mesg[0].split(' ', maxsplit=1)
    name_args = mesg[0].split('|', maxsplit=2)
    qbitsel = False
    try:
        link = message_args[1]
        if link.startswith("s ") or link == "s":
            qbitsel = True
            message_args = mesg[0].split(' ', maxsplit=2)
            link = message_args[2]
        if link.startswith("|") or link.startswith("pswd: "):
            link = ''
    except IndexError:
        link = ''
    try:
        name = name_args[1]
        name = name.strip()
        if "pswd:" in name_args[0]:
            name = ''
    except IndexError:
        name = ''
    try:
        ussr = urllib.parse.quote(mesg[1], safe='')
        pssw = urllib.parse.quote(mesg[2], safe='')
    except:
        ussr = ''
        pssw = ''
    if ussr != '' and pssw != '':
        link = link.split("://", maxsplit=1)
        link = f'{link[0]}://{ussr}:{pssw}@{link[1]}'
    pswd = mesg[0].split('pswd: ')
    if len(pswd) > 1:
        pswd = pswd[1]
    else:
        pswd = None
    link = re.split(r"pswd:|\|", link)[0]
    link = link.strip()
    reply_to = update.message.reply_to_message
    if reply_to is not None:
        file = None
        media_array = [reply_to.document, reply_to.video, reply_to.audio]
        for i in media_array:
            if i is not None:
                file = i
                break
        if (
            not bot_utils.is_url(link)
            and not bot_utils.is_magnet(link)
            or len(link) == 0
        ):
            if file is None:
                reply_text = reply_to.text
                reply_text = reply_text.split('\n')[0]
                if bot_utils.is_url(reply_text) or bot_utils.is_magnet(reply_text):
                    link = reply_text

            elif isQbit:
                file_name = str(time.time()).replace(".", "") + ".torrent"
                link = file.get_file().download(custom_path=file_name)
            elif file.mime_type != "application/x-bittorrent":
                listener = MirrorListener(update, context, pswd, isZip, extract, isLeech=isLeech)
                tg_downloader = TelegramDownloadHelper(listener)
                tg_downloader.add_download(update.message, f'{DOWNLOAD_DIR}{listener.uid}/', name)
                return
            else:
                link = file.get_file().file_path
    if link != '':
        LOGGER.info(link)
    if bot_utils.is_url(link) and not bot_utils.is_magnet(link) and not os.path.exists(link) and isQbit:
        resp = requests.get(link)
        if resp.status_code == 200:
            file_name = str(time.time()).replace(".", "") + ".torrent"
            open(file_name, "wb").write(resp.content)
            link = f"{file_name}"
        else:
            sendMessage(f"ERREUR : le lien a retourné le code HTTP : {resp.status_code}", context.bot, update)
            return

    elif not bot_utils.is_url(link) and not bot_utils.is_magnet(link):
        sendMessage('Aucune source de téléchargement fournie', context.bot, update)
        return
    elif not os.path.exists(link) and not bot_utils.is_mega_link(link) and not bot_utils.is_gdrive_link(link) and not bot_utils.is_magnet(link):
        try:
            link = direct_link_generator(link)
        except DirectDownloadLinkException as e:
            LOGGER.info(e)
            if "ERROR:" in str(e):
                sendMessage(f"{e}", context.bot, update)
                return
            if "Youtube" in str(e):
                sendMessage(f"{e}", context.bot, update)
                return

    listener = MirrorListener(update, context, pswd, isZip, extract, isQbit, isLeech)

    if bot_utils.is_gdrive_link(link):
        if not isZip and not extract and not isLeech:
            sendMessage(f"Utilisez /{BotCommands.CloneCommand} pour cloner un fichier/dossier Google Drive\nUtilisez /{BotCommands.ZipMirrorCommand} pour compresser un dossier Google Drive\nUtilisez /{BotCommands.UnzipMirrorCommand} pour extraire une archive Google Drive", context.bot, update)
            return
        res, size, name, files = gdriveTools.GoogleDriveHelper().helper(link)
        if res != "":
            sendMessage(res, context.bot, update)
            return
        if ZIP_UNZIP_LIMIT is not None:
            LOGGER.info('Vérification de la taille du fichier/dossier...')
            if size > ZIP_UNZIP_LIMIT * 1024**3:
                msg = f'Échec, la limite de compression/décompression est {ZIP_UNZIP_LIMIT}GB.\nLa taille de votre fichier/dossier est {get_readable_file_size(size)}.'
                sendMessage(msg, context.bot, update)
                return
        LOGGER.info(f"Nom du téléchargement : {name}")
        drive = gdriveTools.GoogleDriveHelper(name, listener)
        gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
        download_status = DownloadStatus(drive, size, listener, gid)
        with download_dict_lock:
            download_dict[listener.uid] = download_status
        sendStatusMessage(update, context)
        drive.download(link)

    elif bot_utils.is_mega_link(link):
        if BLOCK_MEGA_LINKS:
            sendMessage("Les liens Mega sont bloqués !", context.bot, update)
            return
        link_type = bot_utils.get_mega_link_type(link)
        if link_type == "folder" and BLOCK_MEGA_FOLDER:
            sendMessage("Les dossiers Mega sont bloqués !", context.bot, update)
        else:
            mega_dl = MegaDownloadHelper()
            mega_dl.add_download(link, f'{DOWNLOAD_DIR}{listener.uid}/', listener)

    elif isQbit and (bot_utils.is_magnet(link) or os.path.exists(link)):
        qbit = QbitTorrent()
        qbit.add_torrent(link, f'{DOWNLOAD_DIR}{listener.uid}/', listener, qbitsel)

    else:
        ariaDlManager.add_download(link, f'{DOWNLOAD_DIR}{listener.uid}/', listener, name)
        sendStatusMessage(update, context)


def mirror(update: Update, context):
    _mirror(update, context)

def unzip_mirror(update: Update, context):
    _mirror(update, context, extract=True)

def zip_mirror(update: Update, context):
    _mirror(update, context, True)

def qb_mirror(update: Update, context):
    _mirror(update, context, isQbit=True)

def qb_unzip_mirror(update: Update, context):
    _mirror(update, context, extract=True, isQbit=True)

def qb_zip_mirror(update: Update, context):
    _mirror(update, context, True, isQbit=True)

def leech(update: Update, context):
    _mirror(update, context, isLeech=True)

def unzip_leech(update: Update, context):
    _mirror(update, context, extract=True, isLeech=True)

def zip_leech(update: Update, context):
    _mirror(update, context, True, isLeech=True)

def qb_leech(update: Update, context):
    _mirror(update, context, isQbit=True, isLeech=True)

def qb_unzip_leech(update: Update, context):
    _mirror(update, context, extract=True, isQbit=True, isLeech=True)

def qb_zip_leech(update: Update, context):
    _mirror(update, context, True, isQbit=True, isLeech=True)

# Création des handlers
mirror_handler = CommandHandler(BotCommands.MirrorCommand, mirror,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
unzip_mirror_handler = CommandHandler(BotCommands.UnzipMirrorCommand, unzip_mirror,
                                      filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
zip_mirror_handler = CommandHandler(BotCommands.ZipMirrorCommand, zip_mirror,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
qb_mirror_handler = CommandHandler(BotCommands.QbMirrorCommand, qb_mirror,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
qb_unzip_mirror_handler = CommandHandler(BotCommands.QbUnzipMirrorCommand, qb_unzip_mirror,
                                      filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
qb_zip_mirror_handler = CommandHandler(BotCommands.QbZipMirrorCommand, qb_zip_mirror,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
leech_handler = CommandHandler(BotCommands.LeechCommand, leech,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
unzip_leech_handler = CommandHandler(BotCommands.UnzipLeechCommand, unzip_leech,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
zip_leech_handler = CommandHandler(BotCommands.ZipLeechCommand, zip_leech,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
qb_leech_handler = CommandHandler(BotCommands.QbLeechCommand, qb_leech,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
qb_unzip_leech_handler = CommandHandler(BotCommands.QbUnzipLeechCommand, qb_unzip_leech,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
qb_zip_leech_handler = CommandHandler(BotCommands.QbZipLeechCommand, qb_zip_leech,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)

# Ajout des handlers à l'application
application.add_handler(mirror_handler)
application.add_handler(unzip_mirror_handler)
application.add_handler(zip_mirror_handler)
application.add_handler(qb_mirror_handler)
application.add_handler(qb_unzip_mirror_handler)
application.add_handler(qb_zip_mirror_handler)
application.add_handler(leech_handler)
application.add_handler(unzip_leech_handler)
application.add_handler(zip_leech_handler)
application.add_handler(qb_leech_handler)
application.add_handler(qb_unzip_leech_handler)
application.add_handler(qb_zip_leech_handler)