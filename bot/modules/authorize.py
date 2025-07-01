from bot.helper.telegram_helper.message_utils import sendMessage
from bot import AUTHORIZED_CHATS, SUDO_USERS, application, DB_URI
from telegram.ext import CommandHandler, ContextTypes
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.db_handler import DbManger
from telegram import Update


async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            msg = 'Utilisateur déjà autorisé'
        elif DB_URI is not None:
            msg = DbManger().db_auth(user_id)
        else:
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{user_id}\n')
            AUTHORIZED_CHATS.add(user_id)
            msg = 'Utilisateur autorisé'
    elif reply_message is None:
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            msg = 'Chat déjà autorisé'
        elif DB_URI is not None:
            msg = DbManger().db_auth(chat_id)
        else:
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{chat_id}\n')
            AUTHORIZED_CHATS.add(chat_id)
            msg = 'Chat autorisé'
    else:
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            msg = 'Utilisateur déjà autorisé'
        elif DB_URI is not None:
            msg = DbManger().db_auth(user_id)
        else:
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{user_id}\n')
            AUTHORIZED_CHATS.add(user_id)
            msg = 'Utilisateur autorisé'
    await sendMessage(msg, context.bot, update)


async def unauthorize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().db_unauth(user_id)
            else:
                AUTHORIZED_CHATS.remove(user_id)
                msg = 'Utilisateur désautorisé'
        else:
            msg = 'Utilisateur déjà désautorisé'
    elif reply_message is None:
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().db_unauth(chat_id)
            else:
                AUTHORIZED_CHATS.remove(chat_id)
                msg = 'Chat désautorisé'
        else:
            msg = 'Chat déjà désautorisé'
    else:
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().db_unauth(user_id)
            else:
                AUTHORIZED_CHATS.remove(user_id)
                msg = 'Utilisateur désautorisé'
        else:
            msg = 'Utilisateur déjà désautorisé'
    with open('authorized_chats.txt', 'w') as file:
        for i in AUTHORIZED_CHATS:
            file.write(f'{i}\n')
    await sendMessage(msg, context.bot, update)


async def addSudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            msg = 'Déjà Sudo'
        elif DB_URI is not None:
            msg = DbManger().db_addsudo(user_id)
        else:
            with open('sudo_users.txt', 'a') as file:
                file.write(f'{user_id}\n')
            SUDO_USERS.add(user_id)
            msg = 'Promu en tant que Sudo'
    elif reply_message is None:
        msg = "Donnez un ID ou répondez au message de la personne à promouvoir"
    else:
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            msg = 'Déjà Sudo'
        elif DB_URI is not None:
            msg = DbManger().db_addsudo(user_id)
        else:
            with open('sudo_users.txt', 'a') as file:
                file.write(f'{user_id}\n')
            SUDO_USERS.add(user_id)
            msg = 'Promu en tant que Sudo'
    await sendMessage(msg, context.bot, update)


async def removeSudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().db_rmsudo(user_id)
            else:
                SUDO_USERS.remove(user_id)
                msg = 'Rétrogradé'
        else:
            msg = "N'est pas un Sudo"
    elif reply_message is None:
        msg = "Donnez un ID ou répondez au message de la personne à retirer des Sudo"
    else:
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().db_rmsudo(user_id)
            else:
                SUDO_USERS.remove(user_id)
                msg = 'Rétrogradé'
        else:
            msg = "N'est pas un Sudo"
    if DB_URI is None:
        with open('sudo_users.txt', 'w') as file:
            for i in SUDO_USERS:
                file.write(f'{i}\n')
    await sendMessage(msg, context.bot, update)


async def sendAuthChats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = '\n'.join(str(id) for id in AUTHORIZED_CHATS)
    sudo = '\n'.join(str(id) for id in SUDO_USERS)
    msg = f'<b><u>Chats autorisés</u></b>\n<code>{user}</code>\n<b><u>Utilisateurs Sudo</u></b>\n<code>{sudo}</code>'
    await sendMessage(msg, context.bot, update)


# Handlers sans run_async
application.add_handler(CommandHandler(BotCommands.AuthorizedUsersCommand, sendAuthChats,
                                       filters=CustomFilters.owner_filter | CustomFilters.sudo_user))
application.add_handler(CommandHandler(BotCommands.AuthorizeCommand, authorize,
                                       filters=CustomFilters.owner_filter | CustomFilters.sudo_user))
application.add_handler(CommandHandler(BotCommands.UnAuthorizeCommand, unauthorize,
                                       filters=CustomFilters.owner_filter | CustomFilters.sudo_user))
application.add_handler(CommandHandler(BotCommands.AddSudoCommand, addSudo,
                                       filters=CustomFilters.owner_filter))
application.add_handler(CommandHandler(BotCommands.RmSudoCommand, removeSudo,
                                       filters=CustomFilters.owner_filter))
