from tcp_send_first_segment_last.send import send_first_segment_last


if __name__ == "__main__":
    print("Sending...")
    payload = b"A" * 0x1100
    payload += b"\n"
    # payload = b"Hello TCP.\n"

    send_first_segment_last("192.168.219.10", 1234, payload)
    # send_first_segment_last("127.0.0.1", 4444, payload)

