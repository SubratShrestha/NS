import socket
import time

def send_single_characteristic(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data)
        result = s.recv(1024)
        print("Received Feedback: ", repr(result))

# send_single_characteristic(HOST, PORT, 'start'.encode('utf-8'))
# send_single_characteristic(HOST, PORT, 'clr_wifi_cfg'.encode('utf-8'))
# time.sleep(1)
#
# send_single_characteristic(HOST, PORT, 'stim_amp:{}'.format(1000).encode('utf-8'))
# time.sleep(1)
#
# send_single_characteristic(HOST, PORT, 'stim_type:{}'.format(0).encode('utf-8'))
# time.sleep(1)
#
# send_single_characteristic(HOST, PORT, 'anodic_cathodic:{}'.format(1).encode('utf-8'))
# time.sleep(1)
#
# send_single_characteristic(HOST, PORT, 'phase_one_time:{}'.format(55).encode('utf-8'))
# time.sleep(1)
#
# send_single_characteristic(HOST, PORT, 'inter_phase_gap:{}'.format(55).encode('utf-8'))
# time.sleep(1)
#
# send_single_characteristic(HOST, PORT, 'inter_stim_delay:{}'.format(55).encode('utf-8'))
# time.sleep(1)
#
# send_single_characteristic(HOST, PORT, 'pulse_num:{}'.format(0).encode('utf-8'))
# time.sleep(0.1)
#
# send_single_characteristic(HOST, PORT, 'pulse_num_in_one_burst:{}'.format(0).encode('utf-8'))
# time.sleep(0.1)
#
# send_single_characteristic(HOST, PORT, 'burst_num:{}'.format(0).encode('utf-8'))
# time.sleep(0.1)
#
# send_single_characteristic(HOST, PORT, 'inter_burst_delay:{}'.format(0).encode('utf-8'))
# time.sleep(0.1)
#
# send_single_characteristic(HOST, PORT, 'ramp_up:{}'.format(0).encode('utf-8'))
# time.sleep(0.1)
#
# send_single_characteristic(HOST, PORT, 'short_electrode:{}'.format(1).encode('utf-8'))
# time.sleep(0.1)
#
# send_single_characteristic(HOST, PORT, 'enable_record:{}'.format(0).encode('utf-8'))
# time.sleep(0.1)
#
# send_single_characteristic(HOST, PORT, 'record_offset:{}'.format(0).encode('utf-8'))
# time.sleep(0.1)
