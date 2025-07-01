import subprocess
from bot import LOGGER, dispatcher
from telegram import ParseMode, Update
from telegram.ext import CommandHandler, ContextTypes
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
import tempfile
import os


async def shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    cmd = message.text.split(' ', 1)
    if len(cmd) == 1:
        await message.reply_text("Aucune commande à exécuter n'a été donnée.")
        return

    cmd = cmd[1]
    # Exécuter la commande shell de façon non bloquante
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()

    reply = ''
    if stdout:
        reply += f"*Sortie standard*\n`{stdout}`\n"
        LOGGER.info(f"Shell - {cmd} - {stdout}")
    if stderr:
        reply += f"*Erreur standard*\n`{stderr}`\n"
        LOGGER.error(f"Shell - {cmd} - {stderr}")

    if len(reply) > 3000:
        # Écrire la sortie dans un fichier temporaire et l'envoyer
        with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write(reply)
            tmp_filepath = tmp_file.name

        await context.bot.send_document(
            chat_id=message.chat_id,
            document=open(tmp_filepath, 'rb'),
            filename=os.path.basename(tmp_filepath),
            reply_to_message_id=message.message_id
        )
        os.remove(tmp_filepath)
    else:
        await message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


shell_handler = CommandHandler(
    BotCommands.ShellCommand,
    shell,
    filters=CustomFilters.owner_filter
)
dispatcher.add_handler(shell_handler)
