import binascii
import uuid
import pygatt
import time

SERIAL_COMMAND_INPUT_CHAR = '0000fe41-8e22-4541-9d4c-21edae82ed19'
FEEDBACK_CHAR = '0000fe42-8e22-4541-9d4c-21edae82ed19'
STREAM_READ_CHAR = '0000fe51-8e22-4541-9d4c-21edae82ed19'

COUNT = 0

def feedback_handler(handle, value):
    global COUNT
    COUNT += 1
    print("COUNT: ", COUNT)
    print("Data: {}".format(value.hex()))
    print("Handle: {}".format(handle))


adapter = pygatt.GATTToolBackend()
adapter.start()
device = adapter.connect("80:E1:26:08:05:56")

response = device.char_write(SERIAL_COMMAND_INPUT_CHAR, bytearray(b'start_recording'), wait_for_response=False)
print("start_recording", response)

device.subscribe(STREAM_READ_CHAR,
                         callback=feedback_handler,
                         indication=False)

time.sleep(300)

adapter.stop()