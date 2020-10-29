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


# import logging
#
# logging.basicConfig()
# logging.getLogger('pygatt').setLevel(logging.DEBUG)

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'little')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'little')


# if '-esp' in sys.argv:
#     SERIAL_COMMAND_INPUT_CHAR = '02000000-0000-0000-0000-000000000101'
# elif '-stm' in sys.argv:
# from consts import SERIAL_COMMAND_INPUT_CHAR, FEEDBACK_CHAR, STREAM_READ_CHAR
SERIAL_COMMAND_INPUT_CHAR = '0000fe41-8e22-4541-9d4c-21edae82ed19'
FEEDBACK_CHAR = '0000fe42-8e22-4541-9d4c-21edae82ed19'
STREAM_READ_CHAR = '0000fe51-8e22-4541-9d4c-21edae82ed19'


# else:
#     print("DEVICE NOT SUPPORTED/SPECIFIED, only allow -stm and -esp")


class BluetoothComms():
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

    #         self.last_activity = time.time()

    async def ble_discover(self, loop, time):
        task1 = loop.create_task(discover(time))
        await asyncio.wait([task1])
        return task1

    async def stream(self, address, loop, data, depth=0):

        stop_event = asyncio.Event()
        fh = open("streaming_data.txt", "a")

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

        # response = device.char_write(SERIAL_COMMAND_INPUT_CHAR, bytearray(b'start_recording'), wait_for_response=False)
        k = SERIAL_COMMAND_INPUT_CHAR
        for v in data[k]:
            device.char_write(k, v, False)  # str(v).encode('utf-8')
            await asyncio.sleep(0.1, loop=loop)
            print("Streaming:sending", v)
        await asyncio.sleep(0.1, loop=loop)

        device.subscribe(STREAM_READ_CHAR,
                         callback=notification_handler,
                         indication=False)

    async def send(self, address, loop, data, depth=0):
        print("SEND")
        try:

            device = self.connected_devices[address]

            k = SERIAL_COMMAND_INPUT_CHAR
            for v in data[k]:
                device.char_write(k, v, False)  # str(v).encode('utf-8')
                await asyncio.sleep(0.1, loop=loop)
                print("Sent:sending", v)
            await asyncio.sleep(0.1, loop=loop)
        except pygatt.exceptions.ExpectedResponseTimeout as e:
            print("pygatt.exceptions.NotConnectedError", e)
            if depth == 0:
                self.connect_to_device(address)
                await self.send(address, loop, data, depth=1)
        except pygatt.backends.bgapi.exceptions.NotConnectedError as e:
            print("pygatt.exceptions.NotConnectedError", e)
            if depth == 0:
                self.connect_to_device(address)
                await self.send(address, loop, data, depth=1)
        except Exception as e:
            print("Exception", e)
            if depth == 0:
                self.connect_to_device(address)
                await self.send(address, loop, data, depth=1)
        else:
            if depth == 0:
                self.connect_to_device(address)
                await self.send(address, loop, data, depth=1)

    async def send_then_read(self, address, loop, data, depth=0):
        print("SEND")
        try:
            device = self.connected_devices[address]

            def notification_handler(sender, data):
                """Simple notification handler which prints the data received."""
                if len(data) == 5:
                    print("notification_handler", sender, data[:1], data[1:])

                    if bytearray(b'\x15') == data[:1]:
                        print("electrode_voltage")

                    self.client_conn.send(
                        {
                            'mac_addr': address,
                            'command': data[:1],
                            'data': data[1:]
                        }
                    )

            device.subscribe(FEEDBACK_CHAR,
                             callback=notification_handler,
                             indication=False, wait_for_response=True)
            await asyncio.sleep(0.1, loop=loop)
            k = SERIAL_COMMAND_INPUT_CHAR
            for v in data[k]:
                device.char_write(k, v, False)  # str(v).encode('utf-8')
                await asyncio.sleep(0.1, loop=loop)
                print("Sent:sending", v)
            await asyncio.sleep(0.1, loop=loop)
            device.unsubscribe(FEEDBACK_CHAR)
        except pygatt.backends.bgapi.exceptions.ExpectedResponseTimeout as e:
            print("pygatt.exceptions.NotConnectedError", e)
            if depth == 0:
                self.connect_to_device(address)
                await self.send_then_read(address, loop, data, depth=1)
        except pygatt.exceptions.NotConnectedError as e:
            print("pygatt.exceptions.NotConnectedError", e)
            if depth == 0:
                self.connect_to_device(address)
                await self.send_then_read(address, loop, data, depth=1)
        except Exception as e:
            print("Exception", e)
            if depth == 0:
                self.connect_to_device(address)
                await self.send_then_read(address, loop, data, depth=1)
        else:
            if depth == 0:
                self.connect_to_device(address)
                await self.send_then_read(address, loop, data, depth=1)

    def r(self, msg, data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(0)
        loop.run_until_complete(self.stream(msg, loop, data))

    def s(self, address, data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(0)
        loop.run_until_complete(self.send(address, loop, data))

    def s_t_r(self, address, data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(0)
        loop.run_until_complete(self.send_then_read(address, loop, data))

    def connect_to_device(self, address):
        device = self.adapter.connect(address)
        # device.exchange_mtu(115)
        self.connected_devices[address] = device

    def is_connected_to_device(self, address):
        return address in self.connected_devices

    def receive_loop(self):
        try:
            address = ('localhost', 6001)
            listener = Listener(address, authkey=b'password')
            conn = listener.accept()

            while self.thread:
                msg = conn.recv()
                if isinstance(msg, str):
                    t = threading.Thread(target=self.r, args=(msg,))
                    # t.start()
                else:
                    send = msg.pop('send')
                    read = msg.pop('read')
                    stream = msg.pop('stream')

                    print("send: ", send)
                    print("read: ", read)
                    print("stream: ", stream)

                    address = msg.pop('mac_addr', None)
                    if address is not None:
                        #                         self.last_activity = time.time()
                        if not self.is_connected_to_device(address):
                            self.connect_to_device(address)

                        if send and stream and not read:
                            data = msg
                            t = threading.Thread(target=self.r, args=(address, data))
                            t.start()

                        elif send and not read:
                            data = msg
                            t = threading.Thread(target=self.s, args=(address, data))
                            t.start()

                        elif send and read:
                            data = msg
                            t = threading.Thread(target=self.s_t_r, args=(address, data))
                            t.start()

            listener.close()
        except Exception as e:
            print(e)

    def disconnect_from_devices(self):
        #         print("disconnect_from_devices")
        for k, v in self.connected_devices.items():
            v.disconnect()
            print("Disconnected Device", k, v)
        self.connected_devices = {}

    #         print("end disconnect from services")

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

                #                 current = time.time()
                #                 difference = int(current-self.last_activity)
                #                 print("since last activity: ", difference)
                #                 if difference > 60:
                #                     self.disconnect_from_devices()

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
                    # for i in data:
                    #     print(i)
                loop.close()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    ble_comms = BluetoothComms()
