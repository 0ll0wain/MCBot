from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
import sys
import time


def ServerWakeUp():
    connection = Connection("ioya.de", username="test")

    def handle_join_game(join_game_packet):
        print('Connected.')

    connection.register_packet_listener(
        handle_join_game, clientbound.play.JoinGamePacket)

    def print_chat(chat_packet):
        print("Message (%s): %s" % (
            chat_packet.field_string('position'), chat_packet.json_data))

    connection.register_packet_listener(
        print_chat, clientbound.play.ChatMessagePacket)

    connection.connect()

    time.sleep(2)
