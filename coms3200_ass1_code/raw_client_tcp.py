import binascii
import socket
import sys
from struct import *


class RawClientTCP:
    def __init__(self):
        self.source_ip = '127.0.0.1'
        self.dest_ip = '127.0.0.1'
        self.source_port = 12345  # do not change this source port
        self.dest_port = None
        self.ip_header = None
        self.tcp_header = None
        self.packet_to_send = None
        self.received_packet = None
        self.msg = b''
        self.raw_socket = None
        self.recv_socket = None
        self.seq_number = 454
        self.ack_number = 0

    def create_raw_socket(self):
        """
        Create a raw socket that sends your crafted TCP packets
        Store the socket in self.raw_socket
        Hint: AF_INET, SOCK_RAW, IPPROTO_RAW
        :return: None
        """
        try:
            self.raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        except socket.error as msg:
            print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    def create_sniffing_socket(self):
        """
        Create a sniffing socket that captures all packets through the network interface
        Store the socket in self.recv_socket
        :return: None
        """
        try:
            s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            # print("Here is the place after trying create sniffing sockets")
        except socket.error as msg:
            print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        s.bind(('lo', 0))  # replace the "lo" with your local network interface
        self.recv_socket = s

    def create_sockets(self):
        """
        Create both raw socket and sniffing socket
        :return: None
        """
        self.create_raw_socket()
        self.create_sniffing_socket()

    def send_out_packet(self):
        """
        Send the crafted packet through the raw socket
        :return: None
        """
        self.raw_socket.sendto(self.packet_to_send, (self.dest_ip, self.dest_port))

    def recv_syn_ack_packet(self):
        """
        Capture the syn-ack packet from the server.
        This function captures every packet from the network interface
        until the packet's flag matches syn_ack flag.
        Store the packet in self.received_packet
        :return: None
        """
        while True:
            syn_ack_packet, _ = self.recv_socket.recvfrom(1024)

            flags = unpack("!H", syn_ack_packet[46:48])[0]  # extract the flag from packet

            if flags == 24594:  # syn-ack flag is 24594
                self.received_packet = syn_ack_packet  # store the syn-ack packet
                break

    def calculate_checksum(self, data):
        """
        Calculate the checksum for tcp header
        :param data: the pseudo header + tcp header + message
        :return: checksum value for  tcp header
        """

        checksum = 0
        # add padding if necessary
        data_len = len(data)
        if data_len % 2:
            data_len += 1
            data += pack('!B', 0)

        # loop taking 2 characters at a time
        for i in range(0, len(data), 2):
            w = (data[i]) + (data[i + 1] << 8)
            checksum = checksum + w

        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum = checksum + (checksum >> 16)

        # complement and mask to 4 byte short
        checksum = ~checksum & 0xffff

        return checksum

    def craft_ip_header(self):
        """
        Create an IP header for the tcp packet
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
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0  # kernel will fill the correct checksum
        ip_saddr = socket.inet_aton(self.source_ip)  # Spoof the source ip address if you want
        ip_daddr = socket.inet_aton(self.dest_ip)

        ip_ihl_ver = (ip_ver << 4) + ip_ihl

        # the ! in the pack format string means network order
        ip_header = pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off,
                         ip_ttl, ip_proto,
                         ip_check,
                         ip_saddr, ip_daddr)
        self.ip_header = ip_header
        return ip_header

    def craft_tcp_header(self, tcp_seq=454, tcp_ack_seq=0, tcp_doff=5, tcp_fin=0, tcp_syn=0, tcp_rst=0,
                         tcp_psh=0, tcp_ack=0, tcp_urg=0, tcp_window=5840, tcp_checksum=0,
                         tcp_urg_ptr=0):
        """
        create a TCP header for the TCP packet
        Need to create a pseudo header before calculate the checksum
        Store the crafted TCP header into self.tcp_header
        :param tcp_seq: the sequence number for the TCP packet
        :param tcp_ack_seq: the acknowledgement number for the TCP packet
        :param tcp_doff: 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        :param tcp_fin: TCP FIN flag
        :param tcp_syn: TCP SYN flag
        :param tcp_rst: TCP RST flag
        :param tcp_psh: TCP PSH flag
        :param tcp_ack: TCP ACK flag
        :param tcp_urg: TCP URG flag
        :param tcp_window: maximum allowed window size
        :param tcp_checksum: TCP packet checksum
        :param tcp_urg_ptr: TCP packet urgent pointer
        :return: None
        """
        # print("in the craft tcp header: tcp_ack_seq: ", tcp_ack_seq)
        # TCP Flags
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

        # TCP Header using struct.pack, network byte order
        tcp_header = pack('!HHLLBBH', self.source_port, self.dest_port, tcp_seq,
                          tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window) + pack(
            'H', tcp_checksum) + pack('!H', tcp_urg_ptr)

        # Pseudo header fields
        source_address = socket.inet_aton(self.source_ip)
        dest_address = socket.inet_aton(self.dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header) + len(self.msg)

        psh = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
        psh = psh + tcp_header + self.msg

        tcp_checksum = self.calculate_checksum(psh)

        # Remake TCP header with correct checksum
        tcp_header = pack('!HHLLBBH', self.source_port, self.dest_port, tcp_seq,
                          tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window) + pack(
            'H', tcp_checksum) + pack('!H', tcp_urg_ptr)

        self.tcp_header = tcp_header
        return tcp_header

    def craft_syn_packet(self):
        """
        Create a syn packet to initial the TCP connection
        Store the crafted syn packet in self.pacekt_to_send
        :return: None
        """
        self.craft_ip_header()
        self.craft_tcp_header(tcp_syn=1)
        self.packet_to_send = self.ip_header + self.tcp_header + self.msg

    def craft_ack_packet(self):
        """
        Create an ack packet to finalise the TCP connection.
        Store the crafted ack packet in self.packet_to_send.
        Hint: Retrieve the sequence number and acknowledgement number from
        the syn-ack packet to figure out the sequence number and acknowledgement
        number for this ack packet.
        :return: None
        """

        # extract the sequence number from the received packet
        server_seq_number = unpack("!I", self.received_packet[38:42])[0]
        self.ack_number = server_seq_number + 1  # sequence number in TCP header
        # print("server seq: ", server_seq_number)
        # extract the acknowledgement number from the received packet
        server_ack_number = unpack("!I", self.received_packet[42:46])[0]
        # print("server ack: ", server_ack_number)
        self.seq_number = server_ack_number  # acknowledgement number in TCP header
        # create the tcp header for an ack packet
        self.craft_ip_header()
        self.craft_tcp_header(tcp_seq=server_ack_number, tcp_ack_seq=server_seq_number + 1, tcp_syn=0, tcp_ack=1)
        self.packet_to_send = self.ip_header + self.tcp_header

    def craft_msg_packet(self, msg):
        """
        Create a psh-ack packet that contains a chat message
        Store the crafted psh-ack packet in self.packet_to_send
        :param msg: chat message
        :return: None
        """
        # Convert the message to bytes
        self.msg = msg.encode()

        # Create the TCP header with the appropriate flags set for a PSH-ACK packet
        self.craft_tcp_header(tcp_seq=self.seq_number, tcp_ack_seq=self.ack_number, tcp_doff=5, tcp_fin=0, tcp_syn=0,
                              tcp_rst=0, tcp_psh=1, tcp_ack=1, tcp_urg=0, tcp_window=5840, tcp_checksum=0,
                              tcp_urg_ptr=0)

        # Create the final packet
        self.packet_to_send = self.ip_header + self.tcp_header + self.msg

        # Update the sequence number
        self.seq_number += len(self.msg)

    def close_sockets(self):
        """
        Close all sockets before exiting the program
        :return: None
        """
        self.raw_socket.close()
        self.recv_socket.close()

    def connect_to_tcp_socket(self):
        """
        The process to establish a TCP connection
        :return: None
        """
        self.create_sockets()
        self.craft_syn_packet()
        self.send_out_packet()
        self.recv_syn_ack_packet()
        self.craft_ack_packet()
        self.send_out_packet()

    def send_msg_to_server(self):
        """
        Send a chat message from stdin to the server
        :return: None
        """
        msg = input("The chat message to send: ")
        if msg:
            self.craft_msg_packet(msg)
            self.send_out_packet()

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

    def run_raw_tcp_client(self):
        """
        Run the raw TCP client to establish a TCP connection and send
        one message to the server
        :return: None
        """
        self.read_port_number()
        self.connect_to_tcp_socket()
        self.send_msg_to_server()
        self.close_sockets()


# the main function
if __name__ == "__main__":
    raw_client_tcp = RawClientTCP()
    raw_client_tcp.run_raw_tcp_client()
