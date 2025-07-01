from speedtest import Speedtest
from bot.helper.telegram_helper.filters import CustomFilters
from bot import dispatcher
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage
from telegram.ext import CommandHandler
import asyncio


async def speedtest(update, context):
    speed = await sendMessage("Lancement du test de vitesse . . . ", context.bot, update)

    def run_speedtest():
        test = Speedtest()
        test.get_best_server()
        test.download()
        test.upload()
        test.results.share()
        return test.results.dict()

    # Exécuter le test dans un thread pour ne pas bloquer l'async loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, run_speedtest)

    string_speed = f'''
<b>Serveur</b>
<b>Nom :</b> <code>{result['server']['name']}</code>
<b>Pays :</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
<b>Sponsor :</b> <code>{result['server']['sponsor']}</code>
<b>Fournisseur d'accès :</b> <code>{result['client']['isp']}</code>

<b>Résultats SpeedTest</b>
<b>Upload :</b> <code>{speed_convert(result['upload'] / 8)}</code>
<b>Download :</b>  <code>{speed_convert(result['download'] / 8)}</code>
<b>Ping :</b> <code>{result['ping']} ms</code>
<b>Note ISP :</b> <code>{result['client']['isprating']}</code>
'''
    await editMessage(string_speed, speed)


def speed_convert(size):
    """Convertit la vitesse en format lisible."""
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "MB/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


SPEED_HANDLER = CommandHandler(
    BotCommands.SpeedCommand,
    speedtest,
    filters=CustomFilters.owner_filter | CustomFilters.authorized_user,
)
dispatcher.add_handler(SPEED_HANDLER)
