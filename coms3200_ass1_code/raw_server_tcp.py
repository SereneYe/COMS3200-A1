import socket
import sys
import time

if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = None
    if len(sys.argv) == 2:
        PORT = int(sys.argv[1])
    else:
        print("Please provide the port number")
        sys.exit(1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT))
        s.listen()
        print("Waiting for connection.")
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")
            while True:
                recvData = conn.recv(1024)
                print(recvData.decode())
