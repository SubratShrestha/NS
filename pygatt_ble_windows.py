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
        """
        Initialize Bluetooth Parameters
        If using the bluetooth dongle, then use BGAPIBackend, otherwise use Gattool Backend for pygatt.
        """
        self.adapter = pygatt.BGAPIBackend()
        self.adapter.start()

        """If prune is true, then it should only show neurostimulator devices, else it shows all devices"""
        self.prune = True  # len(sys.argv) > 1 and "-prune" in sys.argv
        self.thread = True
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.receive_thread.start()
        self.discover_thread = threading.Thread(target=self.ble_discover_loop)
        self.discover_thread.start()
        self.is_recording = False
        self.connected_devices = {}

    async def ble_discover(self, loop, time):
        """
        :param loop:
        :param time:
        :return:
        """
        task1 = loop.create_task(discover(time))
        await asyncio.wait([task1])
        return task1

    def stream(self, address, data):
        """
        :param address:
        :param data:
        :return:

        TODO: The streaming notification handler needs to be redone. It needs to be run in such a manner that other commands are not impeded and also
        that the MTU can be configurable, which is not possible on the BGAPI backend with the current dongle. Either find another BGAPI dongle with an
        MTU of around 120+ or one that is configurable. Then, in the notification handler, parse the byte array returned and then send to the graphing app.
        """

        # stop_event = asyncio.Event()
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

        # get device
        device = self.connected_devices[address]
        # signal to device to start streaming
        k = SERIAL_COMMAND_INPUT_CHAR
        for v in data[k]:
            device.char_write(k, v, False)
            time.sleep(INTER_COMMAND_WAIT_TIME)
            print("Streaming:sending", v)
        time.sleep(INTER_COMMAND_WAIT_TIME)
        # subscribe notifications
        device.subscribe(STREAM_READ_CHAR,
                         callback=notification_handler,
                         indication=False)

    def send_then_read(self, address, data, depth=0):
        """

        :param address: device address
        :param data: data to be send to SERIAL_COMMAND_INPUT_CHAR
        :param depth: how many time to retry before giving up if there's an error
        :return:
        """
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
        """
        TODO: Fix this function as it was previously used to multi-thread the streaming function. Likely no longer needed.
        Recommended solution is to just send the data and subscribe, then unsubscribe for notifcations in two separate calls.
        :param msg:
        :param data:
        :return:
        """
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop.set_debug(0)
        # loop.run_until_complete(self.stream(msg, data))
        self.stream(msg, data)

    def connect_to_device(self, address):
        """
        Try to connect to the device, if there's an error, send to the user app.
        :param address:
        :return:
        """
        try:
            device = self.adapter.connect(address)
            # device.exchange_mtu(115) # requires GattTool Backend
            self.connected_devices[address] = device
        except pygatt.exceptions.NotConnectedError as e:
            print("connect_to_device error:", e)
            self.send_error(address, e)
        except pygatt.backends.bgapi.exceptions.ExpectedResponseTimeout as e:
            print("ExpectedResponseTimeout: ", e)
            # self.send_error(address, e)

    def is_connected_to_device(self, address):
        """Returns whether the given BLE address is already connected to"""
        return address in self.connected_devices

    def receive_loop(self):
        """
        :return:
        """
        try:
            """Initialize the connection to receive data through a socket from the user application."""
            address = ('localhost', 6001)
            listener = Listener(address, authkey=b'password')
            conn = listener.accept()

            while self.thread:

                """Receive user's data"""
                msg = conn.recv()

                """send,read,stream allow us to interpret how to communicate with the device"""
                send = msg.pop('send')
                read = msg.pop('read')
                stream = msg.pop('stream')

                print("send: ", send)
                print("read: ", read)
                print("stream: ", stream)

                """Get device address and connect for the first time if not connected already."""
                address = msg.pop('mac_addr', None)
                if address is not None:
                    if not self.is_connected_to_device(address):
                        print("================ CONNECTING FOR THE FIRST TIME ========================")
                        self.connect_to_device(address)

                    if send and stream and not read:
                        """TODO: Streaming needs to be fixed and run concurrently even though the nofications aren't. No need to multi-thread this."""
                        data = msg
                        t = threading.Thread(target=self.r, args=(address, data))
                        t.start()

                    elif send and read:
                        data = msg
                        self.send_then_read(address, data)

            listener.close()
        except Exception as e:
            print(e)

    def send_error(self, address, e):
        """
        Send error to the user application.
        :param address: device that has an error
        :param e: error msg
        :return:
        """
        self.client_conn.send(
            {
                'mac_addr': address,
                'command': 'error',
                'data': str(e)
            }
        )

    def disconnect_from_devices(self):
        """
        Disconnect from devices,
        replaced by self.adapter.stop() in the exception in ble_discover_loop.
        """
        for k, v in self.connected_devices.items():
            v.disconnect()
            print("Disconnected Device", k, v)
        self.connected_devices = {}

    def ble_discover_loop(self):
        """
        Loop through with an incrementing time delay up until
        10 seconds to search for devices in the surroundings.
        """
        try:
            delay = 0.5
            self.client_address = ('localhost', 6000)
            self.client_conn = Client(self.client_address, authkey=b'password')
            while True:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.set_debug(1)
                """Asychronously search for BLE devices"""
                r1 = loop.run_until_complete(self.ble_discover(loop, delay))
                devices = r1.result()

                if self.prune:
                    """Only search for BLE devices with 'Neuro' in their name"""
                    data = [{'text': str(i.address)} for i in devices if
                            i.address is not None and "Neuro" in str(i)]
                else:
                    data = [{'text': str(i.address)} for i in devices if i.address is not None]
                    """Search for all ble devices"""
                if delay < 10:
                    delay += 1
                if self.client_conn.closed:
                    break
                else:
                    self.client_conn.send(data)
                loop.close()
        except Exception as e:
            """This occurs whenever the socket connection ends. If this occurs, then use self.adapter.stop() to disconnect from the devices."""
            print("Discovery Error", e)
            self.adapter.stop()


if __name__ == '__main__':
    ble_comms = BluetoothComms()
