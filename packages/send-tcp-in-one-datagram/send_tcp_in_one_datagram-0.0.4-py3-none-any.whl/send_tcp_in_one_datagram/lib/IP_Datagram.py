from send_tcp_in_one_datagram.lib.TCP_Segment import TCP_Segment


class IP_Datagram():
    def __init__(self, byte_str):
        self.version = (byte_str[0] & 0xF0) >> 4
        self.IHL = (byte_str[0] & 0xF)
        self.length = int.from_bytes(byte_str[2:4])
        self.tcp_segment = TCP_Segment.from_bytes(byte_str[(self.IHL * 4):])

    def get_tcp_segment(self):
        return self.tcp_segment

