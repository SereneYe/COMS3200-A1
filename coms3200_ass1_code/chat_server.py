import socket
import sys
import time
import threading



class ChatServer:

    def __init__(self):
        self.host = "127.0.0.1"
        self.client_name = None
        self.port = None
        self.socket = None
        self.conn = None

    def read_port_number(self):
        """
        Read the port number from argument, store it to self.port.
        Exit with code 1 if invalid argument is provided.
        :return: None
        """
        if len(sys.argv) != 2:
            print("Usage: python3 chat_server.py <port_number>")
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
        :return: None
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print(f"[({time.strftime('%H:%M:%S')})] Waiting for a connection.")
        except Exception as e:
            print("Error listening on port:", e)
            sys.exit(1)

    def recv_client_connection(self):
        """
        Accept a client connection and store the new
        accepted connection to self.conn.
        Get and store the client name in self.client_name.
        Print the get connection message to the stdout.
        Send the welcome message to the connected client.
        :return: None
        """
        try:
            self.conn, addr = self.socket.accept()
            self.client_name = self.conn.recv(1024).decode()
            print(f"[({time.strftime('%H:%M:%S')})] Get a connection from {self.client_name}")
            self.conn.sendall(
                f"[Server ({time.strftime('%H:%M:%S')})] Welcome to the channel, {self.client_name}".encode())
        except Exception as e:
            print("Error accepting client connection:", e)

    def _receive_and_print_message(self):
        """
        Use a while loop to receive TCP packets from the client and print
        messages to stdout.
        If the message is "exit", print "[Connection Terminated by the client]"
        to stdout. Then close the socket and exit wit code 0.
        :return: None
        """
        while True:
            try:
                data = self.conn.recv(1024).decode()
                if data == "exit":
                    print("[Connection terminated by the client]")
                    self.conn.close()  # closing connection instead of raising an exception
                    return  # end of the thread
                if not data:
                    return
                print(f"[{self.client_name} ({time.strftime('%H:%M:%S')})] {data}")
            except Exception as e:
                #print("Error receiving message:", e)
                return

    def receive_and_print_message(self):
        """
        Multithreading
        :return: None
        """
        threading.Thread(target=self._receive_and_print_message).start()

    def send_message(self):
        """
        Use a while loop to get message from stdin and send out the message
        back to the client.
        If the message is "exit", print "[Connection Terminated by the server]"
        to the stdout. Then close the socket and exit with code 0.
        :return: None
        """
        while True:
            try:
                message = input().strip()
                if not message:
                    continue
                self.conn.sendall(f"[Server ({time.strftime('%H:%M:%S')})] {message}".encode())
                if message == "exit":
                    print("[Connection terminated by the server]")
                    self.conn.close()  # closing connection instead of raising an exception
                    return  # end of the thread
            except Exception as e:
                print("Error sending message:", e)
                return

    def run_chat_server(self):
        """
        Run the chat server that receives and sends messages to the client
        :return: None
        """
        self.read_port_number()
        self.listen_on_port()
        self.recv_client_connection()
        self.receive_and_print_message()
        self.send_message()


if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.run_chat_server()