from echo_server import EchoServer
import socket
import sys


class NumberServer(EchoServer):
    """
    Inherit from echo_server.py
    """
    def __init__(self):
        super().__init__()

    def convert_message(self, recv_data):
        """
        Convert numerical digits into their verbal equivalents
        :param recv_data: data received from the client
        :return: the converted verbal equivalents if numerical
        digits is provided, otherwise return "Invalid message"
        """
        recv_data = recv_data.strip()
        if len(recv_data) == 0:
            return "Invalid Message"
        elif recv_data.isdigit():
            num_to_word = {
                '0': 'zero',
                '1': 'one',
                '2': 'two',
                '3': 'three',
                '4': 'four',
                '5': 'five',
                '6': 'six',
                '7': 'seven',
                '8': 'eight',
                '9': 'nine'
            }
            return num_to_word.get(recv_data, "Invalid message")
        else:
            return "Invalid message"

    def receive_and_send_messages(self):
        """
        Use a while loop to continuously receive, convert and
        send messages to the client.
        :return: None
        """
        while True:
            try:
                data = self.conn.recv(1024).decode()
                if not data:
                    break
                converted_msg = self.convert_message(data)
                self.conn.sendall(converted_msg.encode())
            except Exception as e:
                print("Error receiving/sending message:", e)
                break

    def run_number_server(self):
        """
        Start the number server to receive, convert and
        send back messages to the client
        :return: None
        """
        self.read_port_number()
        self.listen_on_port()
        self.receive_and_send_messages()


if __name__ == '__main__':
    number_server = NumberServer()
    number_server.run_number_server()
