class IceHelper:
    _debug_level = 1  # used to decide what level of debug messages need to be printed

    modes        = [0, 1, 2]

    sever_packet_size  = 1024  # num bytes
    client_packet_size = 64     # num bytes

    @classmethod
    def print_unreliability_mode_info(cls, mode_p=-1):
        def _helper(x):
            if x == 0:
                print(x, ": no error")
            elif x == 1:
                print(x, ": packet corruption/drop")
            elif x == 2:
                print(x, ": packet reorder")
            else:
                print("Fatal error: print_unreliability_mode_info")
                exit(-1)

        if mode_p == -1:
            for mode in cls.modes:
                _helper(mode)
        else:
            _helper(mode_p)

    @classmethod
    def get_n_bytes(cls, conn_socket, n):
        _data = cls.get_n_bytes_raw(conn_socket, n)
        if len(_data) < n:
            ret = ''
        else:
            ret = _data.decode()
        return ret

    @classmethod
    def get_integer_from_socket(cls, conn_socket):
        num_str = ''
        while True:
            c = cls.get_n_bytes(conn_socket, 1)
            if c == '_':
                break
            elif c == '':
                print("The connection terminated")
                return None
            else:
                num_str += c
        return int(num_str)

    @classmethod
    def get_n_bytes_raw(cls, conn_socket, n):
        _data = b''
        while len(_data) < n:
            try:
                _m = conn_socket.recv(n - len(_data))
                if not _m:
                    # client has disconnected
                    _data = b''
                    break
                _data += _m
            except OSError:
                break
        if len(_data) < n:
            _data = b''
        return _data
