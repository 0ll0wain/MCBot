from ServerLogin import ServerWakeUp
from telegram.ext import (
    MessageHandler,
    CommandHandler,
    Updater,
    CallbackContext,
)
import telegram
from mcstatus import MinecraftServer

updater = Updater(
    token='1653554750:AAELwwCTnsIoOM7mffylv9z_kqR0dtKgtO0', use_context=True)
dispatcher = updater.dispatcher


# If you know the host and port, you may skip this and use MinecraftServer("example.org", 1234)
server = MinecraftServer("ioya.de")


def start(update, context):
    update.message.reply_text("Started")


def status(update, context):
    status = server.status()
    update.message.reply_text(
        "The server has {} players".format(status.players.online))


def wakeup(update, context):
    ServerWakeUp()
    update.message.reply_text("Server is starting now!")


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('status', status))
dispatcher.add_handler(CommandHandler('wakeup', wakeup))

updater.start_polling()
