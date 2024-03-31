import socket
import sys

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = None
    if len(sys.argv) == 2:
        PORT = int(sys.argv[1])
    else:
        print("Please provide the port number")
        sys.exit(1)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))

        while True:
            recved_packet, addr = s.recvfrom(1024)
            print(recved_packet.decode())
