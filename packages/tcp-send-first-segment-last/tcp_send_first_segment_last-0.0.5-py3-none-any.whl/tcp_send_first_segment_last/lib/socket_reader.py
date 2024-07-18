import errno
import socket
import time

from tcp_send_first_segment_last.lib.IP_Datagram import IP_Datagram



# Assumes the socket is non-blocking
# From https://stackoverflow.com/a/16745561/5832619
def read_responses(sock, dst_port):
    dgrams = []

    try:
        while True:
            data = sock.recv(1024)
            ip_datagram = IP_Datagram.from_bytes(data)
            tcp_segment = ip_datagram.get_tcp_segment()
            if tcp_segment.get_dst_port() == dst_port:
                dgrams.append(ip_datagram)
    except socket.error as e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            if len(dgrams) > 0:
                return dgrams
            else:
                time.sleep(1)
                return read_responses(sock, dst_port)
        else:
            raise e

