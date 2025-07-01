from mega import Mega
import os
import threading
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage
from bot.helper.ext_utils.bot_utils import new_thread, get_readable_file_size

class MegaDownloadHelper:
    def __init__(self):
        self.mega = Mega()
        self.m = None

    def login(self, email=None, password=None):
        if email and password:
            self.m = self.mega.login(email, password)
        else:
            self.m = self.mega.login()

    @new_thread
    def add_download(self, mega_link: str, path: str, listener):
        if not self.m:
            self.login()  # Ou login avec identifiants config

        if not os.path.exists(path):
            os.makedirs(path)

        try:
            # Téléchargement simple, bloque ici jusqu'à fin du download
            filename = self.m.download_url(mega_link, dest_filename=path)
            msg = f"Téléchargement terminé : {filename}"
            sendMessage(msg, listener.bot, listener.update)
        except Exception as e:
            sendMessage(f"Erreur Mega: {str(e)}", listener.bot, listener.update)
