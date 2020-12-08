from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
import asyncio
import threading
from multiprocessing.connection import Listener, Client
import sys
import ast
import time
from bitstring import BitArray
import csv
import pygatt
from consts import *


class BluetoothComms:
    def __init__(self):
        self.adapter = pygatt.BGAPIBackend()
        self.adapter.start()
        self.prune = True  # len(sys.argv) > 1 and "-prune" in sys.argv
        self.thread = True
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.receive_thread.start()
        self.discover_thread = threading.Thread(target=self.ble_discover_loop)
        self.discover_thread.start()
        self.is_recording = False
        self.connected_devices = {}

    async def ble_discover(self, loop, time):
        task1 = loop.create_task(discover(time))
        await asyncio.wait([task1])
        return task1

    async def stream(self, address, data):

        stop_event = asyncio.Event()
        # fh = open("streaming_data.txt", "a")

        def notification_handler(sender, not_data):
            """Simple notification handler which prints the data received."""

            print(sender, not_data)
            # n = 16
            #
            # bytes_as_bits = ''.join(format(byte, '08b') for byte in data)
            # bytes_as_bits = str(bytes_as_bits)
            #
            # bitstring = [bytes_as_bits[i:i + n] for i in range(0, len(bytes_as_bits), n)]
            # endian_on_last = False
            # if endian_on_last:
            #     last = str(bitstring.pop())
            #     f_half = last[:8]
            #     s_half = last[8:]
            #
            #     print(last, f_half, s_half)
            #     last = str(s_half) + str(f_half)
            #     bitstring.append(last)
            #
            # result = []
            # for bits in bitstring:
            #     if not endian_on_last:
            #         f_half = bits[:8]
            #         s_half = bits[8:]
            #         bits = str(s_half) + str(f_half)
            #
            #     result.append(int(bits, 2))
            #
            # for i in data:
            #     fh.write(str(i) + '\n')
            #
            # self.client_conn.send(
            #     {
            #         'mac_addr': address,
            #         'stream': result  # [int(i) for i in list(data)]
            #     }
            # )

        device = self.connected_devices[address]

        k = SERIAL_COMMAND_INPUT_CHAR
        for v in data[k]:
            device.char_write(k, v, False)
            time.sleep(INTER_COMMAND_WAIT_TIME)
            print("Streaming:sending", v)
        time.sleep(INTER_COMMAND_WAIT_TIME)

        device.subscribe(STREAM_READ_CHAR,
                         callback=notification_handler,
                         indication=False)

    def send_then_read(self, address, data, depth=0):
        print("SEND")
        try:
            device = self.connected_devices[address]

            rssi = device.get_rssi()
            time.sleep(INTER_COMMAND_WAIT_TIME)

            def notification_handler(sender, data):
                """Simple notification handler which prints the data received."""
                if len(data) == 5:
                    print("notification_handler", sender, data[:1], data[1:])

                    if Parameters.electrode_voltage[:1] == data[:1]:
                        print("electrode_voltage")

                    self.client_conn.send(
                        {
                            'mac_addr': address,
                            'command': data[:1],
                            'data': data[1:],
                            'rssi': rssi
                        }
                    )

            device.subscribe(FEEDBACK_CHAR,
                             callback=notification_handler,
                             indication=False, wait_for_response=True)
            time.sleep(INTER_COMMAND_WAIT_TIME)
            k = SERIAL_COMMAND_INPUT_CHAR
            for v in data[k]:
                device.char_write(k, v, False)
                time.sleep(INTER_COMMAND_WAIT_TIME)
                print("Sent:sending", v)
            time.sleep(INTER_COMMAND_WAIT_TIME)
            device.unsubscribe(FEEDBACK_CHAR)
        except pygatt.backends.bgapi.exceptions.ExpectedResponseTimeout as e:
            print("pygatt.exceptions.NotConnectedError", e)
            if depth == 0:
                self.connect_to_device(address)
                self.send_then_read(address, data, depth=1)
            else:
                self.send_error(address, e)
        except pygatt.exceptions.NotConnectedError as e:
            print("pygatt.exceptions.NotConnectedError", e)
            if depth == 0:
                self.connect_to_device(address)
                self.send_then_read(address, data, depth=1)
            else:
                self.send_error(address, e)
        except Exception as e:
            print("Exception", e)
            if depth == 0:
                self.connect_to_device(address)
                self.send_then_read(address, data, depth=1)
            else:
                self.send_error(address, e)

    def r(self, msg, data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(0)
        loop.run_until_complete(self.stream(msg, loop, data))

    def s_t_r(self, address, data):
        self.send_then_read(address, data)

    def connect_to_device(self, address):
        try:
            device = self.adapter.connect(address)
            # device.exchange_mtu(115)
            self.connected_devices[address] = device
        except pygatt.exceptions.NotConnectedError as e:
            print("connect_to_device error:", e)
            self.send_error(address, e)
        except pygatt.backends.bgapi.exceptions.ExpectedResponseTimeout as e:
            print("ExpectedResponseTimeout: ", e)
            # self.send_error(address, e)

    def is_connected_to_device(self, address):
        return address in self.connected_devices

    def receive_loop(self):
        try:
            address = ('localhost', 6001)
            listener = Listener(address, authkey=b'password')
            conn = listener.accept()

            while self.thread:
                msg = conn.recv()

                send = msg.pop('send')
                read = msg.pop('read')
                stream = msg.pop('stream')

                print("send: ", send)
                print("read: ", read)
                print("stream: ", stream)

                address = msg.pop('mac_addr', None)
                if address is not None:
                    if not self.is_connected_to_device(address):
                        print("================ CONNECTING FOR THE FIRST TIME ========================")
                        self.connect_to_device(address)

                    if send and stream and not read:
                        data = msg
                        t = threading.Thread(target=self.r, args=(address, data))
                        t.start()

                    elif send and read:
                        data = msg
                        self.s_t_r(address, data)

            listener.close()
        except Exception as e:
            print(e)

    def disconnect_from_devices(self):
        for k, v in self.connected_devices.items():
            v.disconnect()
            print("Disconnected Device", k, v)
        self.connected_devices = {}

    def ble_discover_loop(self):
        try:
            delay = 0.5
            self.client_address = ('localhost', 6000)
            self.client_conn = Client(self.client_address, authkey=b'password')
            while True:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.set_debug(1)
                r1 = loop.run_until_complete(self.ble_discover(loop, delay))
                devices = r1.result()

                if self.prune:
                    data = [{'text': str(i.address)} for i in devices if
                            i.address is not None and "Neuro" in str(i)]
                else:
                    data = [{'text': str(i.address)} for i in devices if i.address is not None]
                if delay < 10:
                    delay += 1
                if self.client_conn.closed:
                    break
                else:
                    self.client_conn.send(data)
                loop.close()
        except Exception as e:
            print("Discovery Error", e)
            self.adapter.stop()


if __name__ == '__main__':
    ble_comms = BluetoothComms()
