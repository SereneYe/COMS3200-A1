import socket
import sys


class EchoServer:

    def __init__(self):
        self.addr = None
        self.port = None
        self.socket = None
        self.host = "127.0.0.1"
        self.conn = None

    def read_port_number(self):
        """
        Read the port number from argument, store it to self.port.
        Exit with status 1 if invalid argument is provided.
        :return: None
        """
        if len(sys.argv) != 2:
            print("Usage: python3 echo_server.py <port_number>")
            sys.exit(1)
        try:
            self.port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number.")
            sys.exit(1)

    def listen_on_port(self):
        """
        Create a socket listens on the specified port.
        Store the socket object to self.socket.
        Store the new accepted connection to self.conn.
        :return: None
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            # print("Server is listening on port", self.port)
            self.conn, self.addr = self.socket.accept()
            # print("Connected to", self.addr)
        except Exception as e:
            print("Error listening on port:", e)
            sys.exit(1)

    def receive_message(self):
        """
        Receive a TCP packet from the client.
        :return: the received message
        """
        try:
            message = self.conn.recv(1024).decode()
            return message
        except Exception as e:
            print("Error receiving message:", e)

    def send_message(self, msg):
        """
        Send a message back to the client
        :param msg: the message to send to the client
        :return: None
        """
        try:
            self.conn.sendall(msg.encode())
        except Exception as e:
            print("Error sending message:", e)

    def echo_messages(self):
        """
        Use a while loop to echo messages back to client
        :return: None
        """
        while True:
            message = self.receive_message()
            if not message:
                break
            self.send_message(message)

    def run_echo_server(self):
        """
        Run the echo server to receive and echo back messages
        :return: None
        """
        self.read_port_number()
        self.listen_on_port()
        self.echo_messages()


if __name__ == "__main__":
    echo_server = EchoServer()
    echo_server.run_echo_server()
