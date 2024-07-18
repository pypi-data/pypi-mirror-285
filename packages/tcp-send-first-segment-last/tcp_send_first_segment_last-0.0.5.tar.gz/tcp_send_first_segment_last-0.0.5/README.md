
# tcp-send-first-segment-last

## Purpose

Not all applications receive data off the network correctly, and they
can miss key chunks of data even when they don't mean to. As an example,
Python's [socket.recv](https://docs.python.org/3/library/socket.html#socket.socket.recv)
needs to be called repeatedly until all data has been received. But,
if the receiving application doesn't properly loop, then it may miss
key data later in the buffer.

This library ensures that all data will be in the receiving buffer
before the receiving application begins reading the data. It does
this by sending the TCP segments out of order; and in particular,
it does this by sending the first TCP segment last.

By sending the first TCP segment last, all the later segments will
already be waiting in the receiving buffer by the time that the
first segment arrives. Then, if the receiving application only
calls Python's `socket.recv` function once, it will still read
all of the intended data.

I first encountered this issue while working on the EXP-301 course
from OffSec (a course that focuses on exploiting applications
via buffer overflows). And I created this library to help solve
labs and challenges from this course.

## Usage

PyPi project: https://pypi.org/project/tcp-send-first-segment-last/

```bash
$ pip install tcp-send-first-segment-last
```

```python
from tcp_send_first_segment_last.send import send_first_segment_last


payload = b"A" * 5000

send_first_segment_last("127.0.0.1", 4444, payload)
```

## Current Implementation

* The current implementation waits 5 seconds before sending the final (first) segment, and waits another 5 seconds before closing the connection
* Payloads are currently broken up into 1000 byte chunks

## Known Drawbacks

* Only supports IP addresses, does not support hostnames
* Only runs on Linux/Unix
* Modifies 'iptables' to disable the default RST response from the OS when receiving a response from the target application
* Chunk size is not currently modifiable
* Wait time before sending the first packet is not modifiable
* Must be `root` to run

