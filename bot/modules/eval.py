import io
import os
import textwrap
import traceback
from contextlib import redirect_stdout

from telegram import Update, constants
from telegram.ext import CommandHandler, ContextTypes

from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage
from bot import LOGGER, application

namespaces = {}


def namespace_of(chat, update, bot):
    if chat not in namespaces:
        namespaces[chat] = {
            '__builtins__': globals()['__builtins__'],
            'bot': bot,
            'effective_message': update.effective_message,
            'effective_user': update.effective_user,
            'effective_chat': update.effective_chat,
            'update': update
        }
    return namespaces[chat]


def log_input(update: Update):
    user = update.effective_user.id
    chat = update.effective_chat.id
    LOGGER.info(f"IN: {update.effective_message.text} (user={user}, chat={chat})")


async def send(msg, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(str(msg)) > 2000:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "output.txt"
            await context.bot.send_document(
                chat_id=update.effective_chat.id, document=out_file)
    else:
        LOGGER.info(f"OUT: '{msg}'")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"`{msg}`",
            parse_mode=constants.ParseMode.MARKDOWN)


async def evaluate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send(do(eval, update, context), update, context)


async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send(do(exec, update, context), update, context)


def cleanup_code(code):
    if code.startswith('```') and code.endswith('```'):
        return '\n'.join(code.split('\n')[1:-1])
    return code.strip('` \n')


def do(func, update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_input(update)
    content = update.message.text.split(' ', 1)[-1]
    body = cleanup_code(content)
    env = namespace_of(update.message.chat_id, update, context.bot)

    os.chdir(os.getcwd())
    with open(os.path.join(os.getcwd(), 'bot/modules/temp.txt'), 'w') as temp:
        temp.write(body)

    stdout = io.StringIO()
    to_compile = f'def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return f'{e.__class__.__name__}: {e}'

    func_ = env['func']

    try:
        with redirect_stdout(stdout):
            func_return = func_()
    except Exception as e:
        value = stdout.getvalue()
        return f'{value}{traceback.format_exc()}'
    else:
        value = stdout.getvalue()
        result = None
        if func_return is None:
            if value:
                result = f'{value}'
            else:
                try:
                    result = f'{repr(eval(body, env))}'
                except:
                    pass
        else:
            result = f'{value}{func_return}'
        return result if result else "No output."


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_input(update)
    global namespaces
    if update.message.chat_id in namespaces:
        del namespaces[update.message.chat_id]
    await send("Cleared locals.", update, context)


async def exechelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_string = '''
<b>Executor</b>
• /eval <i>Run Python Code Line | Lines</i>
• /exec <i>Run Commands In Exec</i>
• /clearlocals <i>Cleared locals</i>
'''
    await sendMessage(help_string, context.bot, update)


# Handlers

application.add_handler(CommandHandler(
    'eval', evaluate, filters=CustomFilters.owner_filter))

application.add_handler(CommandHandler(
    'exec', execute, filters=CustomFilters.owner_filter))

application.add_handler(CommandHandler(
    'clearlocals', clear, filters=CustomFilters.owner_filter))

application.add_handler(CommandHandler(
    BotCommands.ExecHelpCommand, exechelp, filters=CustomFilters.owner_filter))
