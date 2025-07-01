from telegram.ext import filters
from telegram import Message
from bot import AUTHORIZED_CHATS, SUDO_USERS, OWNER_ID, download_dict, download_dict_lock


class CustomFilters:
    class _OwnerFilter(filters.MessageFilter):
        def filter(self, message: Message) -> bool:
            return message.from_user and message.from_user.id == OWNER_ID

    owner_filter = _OwnerFilter()

    class _AuthorizedUserFilter(filters.MessageFilter):
        def filter(self, message: Message) -> bool:
            user_id = message.from_user.id if message.from_user else None
            return user_id in AUTHORIZED_CHATS or user_id in SUDO_USERS or user_id == OWNER_ID

    authorized_user = _AuthorizedUserFilter()

    class _AuthorizedChat(filters.MessageFilter):
        def filter(self, message: Message) -> bool:
            return message.chat and message.chat.id in AUTHORIZED_CHATS

    authorized_chat = _AuthorizedChat()

    class _SudoUser(filters.MessageFilter):
        def filter(self, message: Message) -> bool:
            user_id = message.from_user.id if message.from_user else None
            return user_id in SUDO_USERS

    sudo_user = _SudoUser()

    class _MirrorOwner(filters.MessageFilter):
        def filter(self, message: Message) -> bool:
            user_id = message.from_user.id if message.from_user else None
            if user_id == OWNER_ID:
                return True
            args = str(message.text).split(' ') if message.text else []
            if len(args) > 1:
                with download_dict_lock:
                    for status in download_dict.values():
                        if status.gid() == args[1] and status.message.from_user.id == user_id:
                            return True
                    else:
                        return False
            if not message.reply_to_message and len(args) == 1:
                return True
            if message.reply_to_message:
                reply_user = message.reply_to_message.from_user.id
                return reply_user == user_id
            return False

    mirror_owner_filter = _MirrorOwner()
