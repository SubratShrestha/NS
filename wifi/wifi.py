import sys
import time
import socket
import threading

# lanscan checkport and lookup: https://github.com/sperrbit/lanscan

def send_single_characteristic(host, port, data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5) # wait up to 5 seconds
            s.connect((host, port))
            s.sendall(data.encode('utf-8'))
            result = s.recv(1024)
            print("Received Feedback: ", repr(result))
            return result.decode('utf-8')
    except Exception as e:
        print("send_single_characteristic Exception: ", e)
        return None
    except socket.timeout:
        return None

# Portscan
def checkPort(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.01)
        result = s.connect((ip, port))
        s.shutdown(1)
        return True
    except:
        return False

# Reverse Lookup
def lookup(addr):
    try:
        data = socket.gethostbyaddr(str(addr))
        host = repr(data[0])
        host = str(host)
        host = host.strip("'")
        return host
    except:
        return "NA"

def wifi_scan():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    HOST = s.getsockname()[0]
    s.close()
    HOST = HOST.split('.')
    HOST = '.'.join(HOST[:-1])

    result = []

    for i in range(256):
        addy = "{}.{}".format(HOST,str(i))
        port = 8888
        host = lookup(addy)
        listening = checkPort(addy, port)
        if "NeuroStim" in host and listening:
            if host not in result:
                result.append({'text': addy})

    print("wifi_scan: ", result)
    time.sleep(10)
    return result
