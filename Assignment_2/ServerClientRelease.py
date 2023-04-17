import os
import sys
import time
from zlib import crc32
from _socket import SHUT_RDWR
from socket import socket, AF_INET, SOCK_STREAM

from IceHelperRelease import IceHelper


class ServerClient:
    ice_helper          = IceHelper()
    packet_size_server  = ice_helper.sever_packet_size
    packet_size_client  = ice_helper.client_packet_size

    debug_level = 1

    def ice_debug(self, level, *arg):
        if level <= self.debug_level:
            for a in arg:
                print(a, end=' ')
            print()

    def ice_print(self, *arg):
        # ANSI colors
        _c = (
            "\033[0m",  # End of color
            "\033[36m",  # Cyan
            "\033[91m",  # Red
            "\033[35m",  # Magenta
        )

        if self.is_server:
            print(_c[1] + self.secret_student_id + ' Server:' + _c[0], end=' ')
        else:
            print(_c[2] + self.secret_student_id + ' Client:' + _c[0], end=' ')
        for a in arg:
            print(a, end=' ')
        print()

    def __init__(self, argv, is_server):
        if len(argv) < 6:
            print("missing command line parameter: ip_address port_number out_filename mode Student_id")
            self.ice_helper.print_unreliability_mode_info()
            exit(-1)

        i = 1
        self.ip_address          = str(sys.argv[i])
        i += 1
        self.port_number         = int(sys.argv[i])
        i += 1
        self.filename            = str(sys.argv[i])
        i += 1
        mode                     = int(sys.argv[i])
        i += 1
        self.secret_student_id   = str(sys.argv[i])

        self.is_server = is_server

        # open connection
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((self.ip_address, self.port_number))

        # perform handshake
        self.handshake()

        # we can start transmitting the file now
        self.mode_error          = False
        self.mode_reorder        = False
        self.mode_reliable       = False
        if mode == 0:
            self.mode_reliable      = True
        elif mode == 1:
            self.mode_error         = True
        elif mode == 2:
            self.mode_reorder       = True
        else:
            print("ServerClient init: invalid mode")
            exit(-1)

    '''
    This is a complete code, no need to change the function!
    '''
    def handshake(self):
        # initial handshake is to pass the secret key
        # to which the server response with an ok
        # 'C' implies client
        message = 'STID_'
        if self.is_server:
            message += self.secret_student_id + '_' + 'S'
        else:
            message += self.secret_student_id + '_' + 'C'
        self.ice_print('sending: ' + message)
        self.clientSocket.sendall(message.encode())
        # wait to get a response '0_'
        self.ice_print("waiting for server response")
        while True:
            waiting_list_num = self.ice_helper.get_integer_from_socket(self.clientSocket)
            if waiting_list_num is None:
                exit(-1)
            self.ice_print("waiting_list_num: ", waiting_list_num)

            if waiting_list_num == 0:
                # we can start transmitting the file now
                break

    '''
    This is a complete code, no need to change the function!
    '''
    def send_file(self):
        if not self.is_server:
            self.ice_print("Client cannot send file")
            return

        if self.mode_reliable:
            self.send_file_reliable_channel()
        elif self.mode_reorder:
            self.send_file_reorder_channel()
        elif self.mode_error:
            self.send_file_error_channel()
        else:
            print("ServerClient send_file: invalid_mode")
            exit(-1)

    '''
    This is a complete code, no need to change the function!
    '''
    def recv_file(self):
        if self.is_server:
            self.ice_print("Server cannot receive file")
            return

        # time taken estimated
        tic = time.time()

        if self.mode_reliable:
            self.recv_file_reliable_channel()
        elif self.mode_reorder:
            self.recv_file_reorder_channel()
        elif self.mode_error:
            self.recv_file_error_channel()
        else:
            print("ServerClient recv_file: invalid_mode")
            exit(-1)

        elapsed_time = time.time() - tic
        print("\n\n Elapsed time: ", elapsed_time, " Sec\n\n")

    def check_error(self, packet: bytes):
        # True if all good
        checksum = packet[:10].decode()
        test = str(crc32(packet[10:]))
        while len(test) < 10:
            test = '0' + test
        return checksum == test

    def send_ack(self, data: str):
        msg = data
        while len(msg) < self.ice_helper.client_packet_size - 10:
            msg += "0"
        self.clientSocket.sendall(self.add_checksum(msg.encode()))

    def add_checksum(self, packet: bytes):
        checksum = str(crc32(packet))
        #print(checksum)
        while len(checksum) < 10:
            checksum = '0' + checksum
        return checksum.encode() + packet
    
    '''
    File reception over Channel with packet errors
    '''
    def recv_file_error_channel(self):
        # TODO
        with open(self.filename, "wb") as f_out:
            id_now = 0 # written
            while True:
                packet = self.get_one_packet()
                if self.check_error(packet):
                    header = packet[10:16].decode()
                    check = int(header[0])
                    size = int(header[1:5])
                    id = int(header[5])
                    if id_now == id:
                        self.send_ack("1")
                    else:
                        f_out.write(packet[16:(16+size)])
                        self.send_ack("1")
                        id_now = id
                    if check == 0:
                        break
                else:
                    try:
                        self.send_ack("0")
                    except OSError:
                        break

    '''
    File transmission over Channel with packet errors
    '''
    def send_file_error_channel(self):
        # TODO
        file_size = os.path.getsize(self.filename)
        with open(self.filename, "rb") as f_in:
            data = f_in.read()
            i = 0
            id = 1
            while i < file_size:
                x = min(self.packet_size_server - 16, file_size - i)
                packet = data[i:(i+x)]
                # add header
                header = str(x)
                while len(header) < 4:
                    header = '0' + header
                if i == file_size:
                    header = '0' + header
                else:
                    header = '1' + header
                header += str(id)
                packet = header.encode() + packet
                while len(packet) < self.packet_size_server - 10:
                    packet += ('0').encode()
                self.clientSocket.sendall(self.add_checksum(packet))
                ack = self.get_one_packet()
                if self.check_error(ack):
                    if ack[10:11].decode() == "1":
                        i += x
                        id = (id + 1) % 2

    '''
    File reception over Channel which Reorders packets
    '''
    def recv_file_reorder_channel(self):
        # TODO
        with open(self.filename, "wb") as f_out:
            count = 0
            maks = -1
            can = False
            d = {}
            while True:
                packet = self.get_one_packet()
                header = packet[:11].decode()
                seq = int(header[:6])
                check = int(header[6])
                size = int(header[7:11])
                d[seq] = packet[11:(11+size)]
                while count in d:
                    f_out.write(d[count])
                    d.pop(count)
                    if count == maks:
                        can = True
                        break
                    count = (count + 1) % 1000000
                if check == 0:
                    maks = seq
                if can:
                    break
                

    '''
    File transmission over Channel which Reorders packets
    '''
    def send_file_reorder_channel(self):
        # TODO
        file_size = os.path.getsize(self.filename)
        with open(self.filename, "rb") as f_in:
            data = f_in.read()
            i = 0
            seq = 0
            while i < file_size:
                x = min(self.packet_size_server - 11, file_size - i)
                packet = data[i:(i+x)]
                i += x
                header = str(x)
                while len(header) < 4:
                    header = '0' + header
                if i == file_size:
                    header = '0' + header
                else:
                    header = '1' + header
                strseq = str(seq)
                while len(strseq) < 6:
                    strseq = '0' + strseq
                header = strseq + header
                self.clientSocket.sendall(header.encode())
                while len(packet) < self.packet_size_server - 11:
                    packet += ('0').encode()
                self.clientSocket.sendall(packet)
                seq = (seq + 1) % 1000000

    '''
    File reception over Reliable Channel
    '''
    def recv_file_reliable_channel(self):
        # TODO
        with open(self.filename, "wb") as f_out:
            while True:
                packet = self.get_one_packet()
                header = packet[:5].decode()
                check = int(header[0])
                size = int(header[1:5])
                f_out.write(packet[5:(5+size)])
                if check == 0:
                    break

    '''
    File transmission over Reliable Channel
    '''
    def send_file_reliable_channel(self):
        # TODO
        file_size = os.path.getsize(self.filename)
        with open(self.filename, "rb") as f_in:
            data = f_in.read()
            i = 0
            while i < file_size:
                x = min(self.packet_size_server - 5, file_size - i)
                packet = data[i:(i+x)]
                i += x
                # add payload size
                header = str(x)
                while len(header) < 4:
                    header = '0' + header
                # add check
                if i == file_size:
                    header = '0' + header
                else:
                    header = '1' + header
                self.clientSocket.sendall(header.encode())
                while len(packet) < self.packet_size_server - 5:
                    packet += ('0').encode()
                self.clientSocket.sendall(packet)

    # ######## Helper #############
    # This is a complete code, no need to change the function!
    def get_one_packet(self):
        # server receives packet from client and vice versa
        if self.is_server:
            packet = self.ice_helper.get_n_bytes_raw(self.clientSocket, self.packet_size_client)
        else:
            packet = self.ice_helper.get_n_bytes_raw(self.clientSocket, self.packet_size_server)

        return packet

    @staticmethod
    # This is a complete code, no need to change the function!
    def _print_data_hex(data, delay=0.0):
        print('-----', len(data), '-------')
        print(data.hex())
        time.sleep(delay)

    # This is a complete code, no need to change the function!
    def terminate(self):
        try:
            self.clientSocket.shutdown(SHUT_RDWR)
            self.clientSocket.close()
        except OSError:
            # the socket may be already closed
            pass
