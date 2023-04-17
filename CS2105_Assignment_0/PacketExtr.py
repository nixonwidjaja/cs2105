import sys

while True:
    header = sys.stdin.buffer.read1(6)
    if len(header) == 0:
        break
    size = 0
    while True:
        s = sys.stdin.buffer.read1(1).decode()
        if s == 'B':
            break
        size = size * 10 + int(s)
    while size > 0:
        data = sys.stdin.buffer.read1(min(size, 1024 * 1024))
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        size -= len(data)