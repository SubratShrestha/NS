import sys
import time
import socket
import threading

def send_single_characteristic(host, port, data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5) # wait up to 5 seconds
            s.connect((host, port))
            s.sendall(data.encode('utf-8'))
            result = s.recv(1024)
            print("Received Feedback: ", repr(result))
            return result
    except Exception as e:
        print("send_single_characteristic Exception: ", e)
        return None
    except socket.timeout:
        return None

