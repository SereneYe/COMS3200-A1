import socket
import sys
from struct import *


class RawClientUDP:
    def __init__(self):
        self.source_ip = '127.0.0.1'
        self.dest_ip = '127.0.0.1'
        self.source_port = 12345    # do not change this source port
        self.dest_port = 4488   # an arbitrary port
        self.ip_header = None
        self.udp_header = None
        self.packet = None
        self.socket = None
        self.msg = b''

    def create_socket(self):
        """
        Create a raw UDP socket to send crafted UDP packet to the server
        Store the socket in self.socket.
        Hint: AF_INET, SOCK_RAW, IPPROTO_UDP
        :return:None
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

    def send_out_packet(self):
        """
        Send the crafted packet to the destination ip and destination port
        :return: None
        """
        self.socket.sendto(self.packet, (self.dest_ip, self.dest_port))

    def calculate_checksum(self, data):
        """
        Calculate the checksum value for UDP header
        :param data: pseudo header + udp header + message
        :return: The checksum value for UDP header
        """
        checksum = 0
        data_len = len(data)
        if data_len % 2:
            data_len += 1
            data += pack('!B', 0)

        for i in range(0, data_len, 2):
            w = (data[i] << 8) + (data[i + 1])
            checksum += w

        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum = ~checksum & 0xFFFF
        return checksum

    def craft_ip_header(self):
        """
        Create an IP header for the udp packet
        Store the crafted IP header in self.ip_header
        :return: None
        """
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 0  # kernel will fill the correct total length
        ip_id = 54321  # ID of this packet
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_UDP
        ip_check = 0  # kernel will fill the correct checksum
        ip_saddr = socket.inet_aton(self.source_ip)  # Spoof the source ip address if you want to
        ip_daddr = socket.inet_aton(self.dest_ip)

        ip_ihl_ver = (ip_ver << 4) + ip_ihl

        # the ! in the pack format string means network order
        ip_header = pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len,
                         ip_id, ip_frag_off, ip_ttl, ip_proto,
                         ip_check,
                         ip_saddr, ip_daddr)
        self.ip_header = ip_header
        return ip_header

    def craft_udp_header(self):
        """
        Create a UDP header for the UDP packet
        Store the UDP header in self.udp_header
        :return: None
        """
        source_port = self.source_port
        dest_port = self.dest_port
        udp_len = 8 + len(self.msg)
        udp_checksum = 0

        udp_header = pack('!HHHH', source_port, dest_port, udp_len, udp_checksum)

        # create pseudo header
        src_addr = socket.inet_aton(self.source_ip)
        dest_addr = socket.inet_aton(self.dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_UDP
        udp_len_packed = pack('!H', udp_len)
        udp_len_unpacked = unpack('!H', udp_len_packed)[0]  # extract the integer

        pseudo_header = pack('!4s4sBBH', src_addr, dest_addr, placeholder,
                             protocol, udp_len_unpacked)

        checksum = self.calculate_checksum(pseudo_header + udp_header + self.msg)
        udp_header = pack('!HHHH', source_port, dest_port, udp_len, checksum)

        self.udp_header = udp_header

    def craft_udp_packet(self):
        """
        Create the UDP packet to send to the server
        Store the UDP packet in self.packet.
        :return: None
        """
        self.craft_udp_header()
        self.packet = self.udp_header + self.msg

    def get_msg(self):
        """
        Read the message to send to the server from stdin
        and store the message in self.msg
        :return: None
        """
        self.msg = input().encode()

    def close_socket(self):
        """
        Close the UDP socket
        :return: None
        """
        self.socket.close()

    def read_port_number(self):
        """
        Read the port number from argument, store it to self.dest_port.
        Exit if invalid argument is provided.
        :return: None
        """
        if len(sys.argv) == 2:
            try:
                self.dest_port = int(sys.argv[1])
                # print(f"The port number is set to {self.dest_port}")
            except ValueError:
                print("Invalid argument. Please provide a valid port number.")
                sys.exit(1)
        else:
            print("Please provide a port number.")
            sys.exit(1)

    def run_udp_client(self):
        """
        Run the raw UDP client to send messages to the server.
        :return: None
        """
        self.read_port_number()
        self.create_socket()

        while True:
            self.get_msg()
            self.craft_udp_packet()
            self.send_out_packet()


if __name__ == "__main__":
    raw_client_udp = RawClientUDP()
    raw_client_udp.run_udp_client()