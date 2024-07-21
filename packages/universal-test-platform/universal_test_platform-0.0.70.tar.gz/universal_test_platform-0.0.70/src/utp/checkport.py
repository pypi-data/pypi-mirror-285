import socket

def isPortUsed(port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',port))
    sock.close()
    if result == 0:
        return True
    else:
        return False
    