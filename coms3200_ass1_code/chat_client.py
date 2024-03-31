import socket
import sys
import time
import threading


class ChatClient:
    def __init__(self):
        self.host = "127.0.0.1"
        self.client_name = None
        self.port = None
        self.socket = None

    def read_port_and_client(self):
        """
        Read the port number and client name from arguments, store them to
        self.port and self.client_name.
        Exit with code 1 if invalid argument is provided.
        :return: None
        """
        if len(sys.argv) != 3:
            print("Usage: python3 chat_client.py <port_number> <client_name>")
            sys.exit(1)
        try:
            self.port = int(sys.argv[1])
            self.client_name = sys.argv[2]
        except ValueError:
            print("Invalid port number.")
            sys.exit(1)

    def connect_to_port(self):
        """
        Create a socket to try to connect to a specified port,
        store the new socket object to self.socket.
        Send the client name to the server when connected
        :return: None
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.sendall(self.client_name.encode())
        except Exception as e:
            print(f"Error connecting to port {self.port}: {e}")
            sys.exit(1)

    def _receive_and_print_message(self):
        """
        Use a while loop to receive TCP packets from the server and print
        the message out to stdout.
        If the message is "exit", exit the program with code 0
        and print out "[Connection Terminated by the server]" to stdout.
        :return: None
        """
        while True:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                if "exit" in data:
                    print("[Connection terminated by the server]")
                    self.socket.close()
                    sys.exit(0)
                else:
                    print(data)
            except Exception as e:
                print("Error receiving message:", e)
                break

    def receive_and_print_message(self):
        """
        Create a new Multithreading
        :return: None
        """
        threading.Thread(target=self._receive_and_print_message).start()

    def send_message(self):
        """
        Use a while loop to read messages from stdin, then convert
        to bytes and send out as a TCP packets.
        If the message is "exit", print out "[Connection Terminated
        by the client]". Close the socket and exit with status 0.
        :return: None
        """
        while True:
            try:
                message = input().strip()
                if not message:
                    continue
                self.socket.sendall(message.encode())
                if message == "exit":
                    print("[Connection terminated by the client]")
                    self.socket.close()
                    sys.exit(0)
            except Exception as e:
                print("Error sending message:", e)
                break

    def run_chat_client(self):
        """
        Start the chat client to send and receive messages with the server
        :return: None
        """
        self.read_port_and_client()
        self.connect_to_port()
        self.receive_and_print_message()
        self.send_message()


if __name__ == "__main__":
    chat_client = ChatClient()
    chat_client.run_chat_client()
