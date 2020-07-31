import sys
import time
import socket
import threading

def send_single_characteristic(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode('utf-8'))
        result = s.recv(1024)
        print("Received Feedback: ", repr(result))
