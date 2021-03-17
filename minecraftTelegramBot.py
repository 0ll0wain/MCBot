from ServerLogin import ServerWakeUp
from telegram.ext import (
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    Updater,
    CallbackContext,
    Filters,
)
import telegram
from mcstatus import MinecraftServer
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
from time import sleep
from datetime import timedelta

SENDMESSAGE = range(1)

updater = Updater(
    token='1653554750:AAELwwCTnsIoOM7mffylv9z_kqR0dtKgtO0', use_context=True)
dispatcher = updater.dispatcher


# If you know the host and port, you may skip this and use MinecraftServer("example.org", 1234)
server = MinecraftServer("ioya.de")


def start(update, context):
    print(update.message.from_user.first_name)
    update.message.reply_text(
        "Hello to the IOYA Minecraft server Bot!\nType /status to see how many players are online.\nType /wakeup to start the server if you want to play soon.")


def status(update, context):
    status = server.status()
    if status.players.online == 0:
        update.message.reply_text(
            "Nobody is online. Type /wakeup to give the server a good morning slap.")
    else:
        query = server.query()
        update.message.reply_text("The server has the following players online: {0}".format(
            ", ".join(query.players.names)))


def wakeup(update, context):
    ServerWakeUp()
    update.message.reply_text("Server is starting now!")


def startChat(update, context):
    connection = Connection("ioya.de", username="belegram." + str(
        update.message.from_user.first_name))
    context.user_data["connection"] = connection

    id = update.effective_chat.id

    def handle_join_game(join_game_packet):
        print("handle_join_Game")
        context.bot.send_message(
            chat_id=id, text='Connected to Corona Land.')

    connection.register_packet_listener(
        handle_join_game, clientbound.play.JoinGamePacket)

    def print_chat(chat_packet):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Message (%s): %s" % (
            chat_packet.field_string('position'), chat_packet.json_data))

    connection.register_packet_listener(
        print_chat, clientbound.play.ChatMessagePacket)

    connection.connect()
    print("4")
    return SENDMESSAGE


def quitChat(update, context):
    print("5")
    connection = context.user_data["connection"]
    context.user_data.pop("connection")
    print("6")
    connection.disconnect()
    update.message.reply_text("Disconnected from Corona Land.")
    print("7")
    return ConversationHandler.END


def sendMessage(update, context):
    print("8")
    connection = context.user_data["connection"]

    packet = serverbound.play.ChatPacket()
    packet.message = update.message.text
    connection.write_packet(packet)
    print("9")
    return SENDMESSAGE


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('status', status))
dispatcher.add_handler(CommandHandler('wakeup', wakeup))
dispatcher.add_handler(CommandHandler('send', sendMessage))

convServerChat_handler = ConversationHandler(
    entry_points=[CommandHandler("startChat", startChat)],
    states={
        SENDMESSAGE: [
            MessageHandler(Filters.text & (~Filters.command), sendMessage),
        ],
        ConversationHandler.TIMEOUT: [
            MessageHandler(Filters.text & Filters.command, quitChat),
        ],
    },
    fallbacks=[CommandHandler("quit", quitChat)],
    conversation_timeout=timedelta(minutes=5)
)
dispatcher.add_handler(convServerChat_handler)

updater.start_polling()
