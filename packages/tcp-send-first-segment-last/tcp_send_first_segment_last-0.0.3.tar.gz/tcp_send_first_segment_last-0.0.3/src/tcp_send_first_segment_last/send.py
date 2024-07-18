import fcntl
import os
import random
import socket
import time

from tcp_send_first_segment_last.lib.disable_auto_rst import disable, cleanup
from tcp_send_first_segment_last.lib.IP_Datagram import IP_Datagram
from tcp_send_first_segment_last.lib.socket_reader import read_responses
from tcp_send_first_segment_last.lib.TCP_Segment import TCP_Segment
from tcp_send_first_segment_last.lib.TCP_Flags import TCP_Flags



def reset_connection(
        sock, src_addr, dst_addr, src_port, dst_port):
    # Send Rst packet
    flags = TCP_Flags()
    flags.set_rst_flag(True)
    req_segment = TCP_Segment(src_port, dst_port, 0, 0, flags)
    sock.sendall(req_segment.get_bytes(src_addr, dst_addr))

def establish_connection(
        sock, src_addr, dst_addr, src_port, dst_port):
    seq_num = int.from_bytes(random.randbytes(4))

    # Send Syn packet
    flags = TCP_Flags()
    flags.set_syn_flag(True)
    req_segment = TCP_Segment(src_port, dst_port, seq_num, 0, flags)
    sock.sendall(req_segment.get_bytes(src_addr, dst_addr))

    # Receive Syn-Ack
    res_dgrams = read_responses(sock, src_port)
    res_dgram = res_dgrams[0]
    res_segment = res_dgram.get_tcp_segment()
    flags = res_segment.get_flags()
    if not flags.get_syn_flag():
        seq_num = res_segment.get_ack_num()
        ack_num = res_segment.get_seq_num()
        terminate_connection(
                sock, src_addr, dst_addr, src_port, dst_port, seq_num, ack_num)
        return establish_connection(
                sock, src_addr, dst_addr, src_port, dst_port)

    # Send Ack packet
    flags = TCP_Flags()
    flags.set_ack_flag(True)
    seq_num = res_segment.get_ack_num()
    ack_num = res_segment.get_seq_num() + 1
    req_segment = TCP_Segment(src_port, dst_port, seq_num, ack_num, flags)
    sock.sendall(req_segment.get_bytes(src_addr, dst_addr))

    return (seq_num, ack_num)

def terminate_connection(
        sock, src_addr, dst_addr, src_port, dst_port,
        seq_num, ack_num, fin_ack_received = False):
    if fin_ack_received:
        ack_num += 1

    # Send Fin-Ack packet
    flags = TCP_Flags()
    flags.set_fin_flag(True)
    # For some reason, closing the connection doesn't work without this
    flags.set_ack_flag(True)
    req_segment = TCP_Segment(src_port, dst_port, seq_num, ack_num, flags)
    sock.sendall(req_segment.get_bytes(src_addr, dst_addr))

    # Receive Fin-Ack
    res_dgrams = read_responses(sock, src_port)
    res_dgram = res_dgrams[0]
    res_segment = res_dgram.get_tcp_segment()

    if not fin_ack_received:
        # Send Ack packet
        flags = TCP_Flags()
        flags.set_ack_flag(True)
        seq_num = res_segment.get_ack_num()
        ack_num = res_segment.get_seq_num() + 1
        req_segment = TCP_Segment(src_port, dst_port, seq_num, ack_num, flags)
        sock.sendall(req_segment.get_bytes(src_addr, dst_addr))



def send_first_segment_last(dst_addr, dst_port, payload):
    src_port = random.randrange(49152, 65535)

    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    # https://stackoverflow.com/a/16745561/5832619
    fcntl.fcntl(sock, fcntl.F_SETFL, os.O_NONBLOCK)
    sock.connect((dst_addr, dst_port))
    (src_addr, _) = sock.getsockname()

    cleanup()

    # Needed for preventing OS from resetting TCP connection
    disable(src_port)

    (seq_num, ack_num) = establish_connection(
            sock, src_addr, dst_addr, src_port, dst_port)

    first_segment = None
    remaining_segments = []
    chunk_size = 1000
    for i in range(0, len(payload), chunk_size):
        part = payload[i:i+chunk_size]
        set_psh = len(part) < chunk_size

        # Send data
        flags = TCP_Flags()
        flags.set_ack_flag(True)
        flags.set_psh_flag(set_psh)
        req_segment = TCP_Segment(
                src_port, dst_port, seq_num, ack_num, flags, part)
        if i == 0:
            first_segment = req_segment
        else:
            remaining_segments.append(req_segment)
        seq_num += len(part)

    for req_segment in remaining_segments:
        sock.sendall(req_segment.get_bytes(src_addr, dst_addr))

    time.sleep(5) # Sleep for 5 seconds

    sock.sendall(first_segment.get_bytes(src_addr, dst_addr))

    time.sleep(5) # Wait a few seconds before closing connection

    # Receive Ack or Fin-Ack
    res_dgrams = read_responses(sock, src_port)
    res_dgram = res_dgrams[-1]
    res_segment = res_dgram.get_tcp_segment()
    seq_num = res_segment.get_ack_num()
    ack_num = res_segment.get_seq_num()

    fin_ack_received = res_segment.get_flags().get_fin_flag()

    terminate_connection(
            sock, src_addr, dst_addr, src_port, dst_port,
            seq_num, ack_num, fin_ack_received)

    sock.close()
    cleanup()

    return


