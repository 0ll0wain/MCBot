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
import json
import credentials

SENDMESSAGE = range(1)

updater = Updater(
    token=credentials.mcbot_token, use_context=True)
dispatcher = updater.dispatcher


# If you know the host and port, you may skip this and use MinecraftServer("example.org", 1234)
server = MinecraftServer("ioya.de")


def start(update, context):
    update.message.reply_text(
        "Hello to the IOYA Minecraft server Bot!\nType /status to see how many players are online.\nType /wakeup to start the server if you want to play soon.\nWith /startChat you can start to chat with people on the server. Everything you send will be forewarded to the server and backwards.\nWith /quit you can end the chat.")


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
    usr = "tg." + str(update.message.from_user.first_name)
    connection = Connection("ioya.de", username=usr)
    context.user_data["connection"] = connection

    id = update.effective_chat.id

    def handle_join_game(join_game_packet):
        print("handle_join_Game")
        context.bot.send_message(
            chat_id=id, text='Connected to Corona Land.')

    connection.register_packet_listener(
        handle_join_game, clientbound.play.JoinGamePacket)

    def print_chat(chat_packet):
        msg = json.loads(chat_packet.json_data)
        translate = msg["translate"]

        if translate == "chat.type.text":
            name = msg["with"][0]["text"]
            content = msg["with"][1]["text"]
            if name != usr:
                context.bot.send_message(chat_id=update.effective_chat.id, text="%s: %s" % (
                    name, content))

    connection.register_packet_listener(
        print_chat, clientbound.play.ChatMessagePacket)

    connection.connect()
    return SENDMESSAGE


def quitChat(update, context):
    connection = context.user_data["connection"]
    context.user_data.pop("connection")
    connection.disconnect()
    update.message.reply_text("Disconnected from Corona Land.")
    return ConversationHandler.END


def sendMessage(update, context):
    connection = context.user_data["connection"]
    packet = serverbound.play.ChatPacket()
    packet.message = update.message.text
    connection.write_packet(packet)
    return SENDMESSAGE


def respawn(update, context):
    print("respawning...")
    connection = context.user_data["connection"]
    packet = serverbound.play.ClientStatusPacket()
    packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
    connection.write_packet(packet)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('status', status))
dispatcher.add_handler(CommandHandler('wakeup', wakeup))
dispatcher.add_handler(CommandHandler('send', sendMessage))
dispatcher.add_handler(CommandHandler('respawn', respawn))

convServerChat_handler = ConversationHandler(
    entry_points=[CommandHandler("startChat", startChat)],
    states={
        SENDMESSAGE: [
            MessageHandler(Filters.text & (~Filters.command), sendMessage),
        ],
        ConversationHandler.TIMEOUT: [
            MessageHandler(Filters.all, quitChat),
        ],
    },
    fallbacks=[CommandHandler("quit", quitChat)],
    conversation_timeout=timedelta(minutes=5)
)
dispatcher.add_handler(convServerChat_handler)

updater.start_polling()
