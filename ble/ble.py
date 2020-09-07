from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
import asyncio
import threading
from multiprocessing.connection import Listener, Client
import sys
import ast
import time

if '-esp' in sys.argv:
    SERIAL_COMMAND_INPUT_CHAR = '02000000-0000-0000-0000-000000000101'
elif '-stm' in sys.argv:
    SERIAL_COMMAND_INPUT_CHAR = '0000fe41-8e22-4541-9d4c-21edae82ed19'
    FEEDBACK_CHAR = '0000fe42-8e22-4541-9d4c-21edae82ed19'
    STREAM_READ_CHAR = '0000fe51-8e22-4541-9d4c-21edae82ed19'
else:
    print("DEVICE NOT SUPPORTED/SPECIFIED, only allow -stm and -esp")


class BluetoothComms():
    def __init__(self):
        self.prune = len(sys.argv) > 1 and "-prune" in sys.argv
        self.thread = True
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.receive_thread.start()
        self.discover_thread = threading.Thread(target=self.ble_discover_loop)
        self.discover_thread.start()
        self.connected = {}

    async def ble_discover(self, loop, time):
        task1 = loop.create_task(discover(time))
        await asyncio.wait([task1])
        return task1

    async def stream(self, address, loop, depth=0):
        print("STREAM")
        try:
            async with BleakClient(address, loop=loop) as client:
                try:
                    print("Stream:TRY TO CONNECT")
                    await client.connect(timeout=10)
                except Exception as e:
                    print("Stream:Exception", e)
                except BleakDotNetTaskError as e:
                    print("Stream:BleakDotNetTaskError", e)
                except BleakError as e:
                    print("Stream:BleakError", e)
                finally:
                    if await client.is_connected():
                        print("Stream: Connected")
                        stop_event = asyncio.Event()


                        def notification_handler(sender, data):
                            """Simple notification handler which prints the data received."""
                            # print("Notifictation Stream {0}: {1}".format(sender, list(data)))
                            # loop.call_soon_threadsafe(stop_event.set)
                            print("NOTIFICATION")

                        await client.start_notify(STREAM_READ_CHAR, notification_handler)
                        i = 0
                        while True:
                            if not await client.is_connected():
                                await client.connect(timeout=10)
                                print("RECONNECTING")
                                continue
                            await stop_event.wait()
                            print("count: ", i)
                        # await asyncio.sleep(120, loop=loop)

                        # await client.stop_notify(STREAM_READ_CHAR)

                        print("END STREAM")

                        return client

                    print("Stream:NOT CONNECTED")
        except BleakError as e:
            print("Stream:BLEAK ERROR", e)
        if depth < 10:
            depth = depth + 1
            await asyncio.sleep(depth, loop=loop)
            print("Stream:TRY AGAIN")
            return await self.stream(address, loop, depth)
        return None

    async def send(self, address, loop, data, depth=0):
        print("SEND")
        try:
            async with BleakClient(address, loop=loop) as client:
                try:
                    print("Send:TRY TO CONNECT")
                    await client.connect(timeout=10)
                except Exception as e:
                    print("Send:Exception", e)
                except BleakDotNetTaskError as e:
                    print("Send:BleakDotNetTaskError", e)
                except BleakError as e:
                    print("Send:BleakError", e)
                finally:
                    if await client.is_connected():

                        try:
                            print("Send:TRY TO CONNECT")
                            await client.connect(timeout=10)
                        except Exception as e:
                            print("Send:Exception", e)
                        except BleakDotNetTaskError as e:
                            print("Send:BleakDotNetTaskError", e)
                        except BleakError as e:
                            print("Send:BleakError", e)
                        finally:
                            if await client.is_connected():

                                print("Send:CONNECTED", client)
                                if SERIAL_COMMAND_INPUT_CHAR in data:
                                    print("Send:SERIAL COMMAND INPUT")
                                    k = SERIAL_COMMAND_INPUT_CHAR
                                    for v in data[k]:
                                        print("Send:sending", v)
                                        await client.write_gatt_char(k, str(v).encode('utf-8'), False)
                                        await asyncio.sleep(0.05, loop=loop)
                                else:
                                    for k, v in data.items():
                                        print(v)
                                        await client.write_gatt_char(k, str(v).encode('utf-8'), False)
                                        await asyncio.sleep(1, loop=loop)
                                # t = threading.Thread(target=self.r, args=(address,))
                                # t.start()
                            return client
                    print("Send:NOT CONNECTED")
                    return None
        except BleakError as e:
            print("Send:BLEAK ERROR", e)
        if depth < 5:
            depth = depth + 1
            await asyncio.sleep(depth, loop=loop)
            print("Send:SEND AGAIN")
            return await self.send(address, loop, data, depth)
        return None

    async def send_then_read(self, address, loop, data, depth=0):
        print("send_then_read")
        try:
            async with BleakClient(address, loop=loop) as client:
                try:
                    print("send_then_read:TRY TO CONNECT")
                    await client.connect(timeout=10)
                except Exception as e:
                    print("send_then_read:Exception", e)
                except BleakDotNetTaskError as e:
                    print("send_then_read:BleakDotNetTaskError", e)
                except BleakError as e:
                    print("send_then_read:BleakError", e)
                finally:
                    if await client.is_connected():

                        try:
                            print("send_then_read:TRY TO CONNECT")
                            await client.connect(timeout=10)
                        except Exception as e:
                            print("send_then_read:Exception", e)
                        except BleakDotNetTaskError as e:
                            print("send_then_read:BleakDotNetTaskError", e)
                        except BleakError as e:
                            print("send_then_read:BleakError", e)
                        finally:
                            if await client.is_connected():

                                def notification_handler(sender, data):
                                    """Simple notification handler which prints the data received."""
                                    print("Notifictation Stream {0}: {1}".format(sender, list(data)))
                                    self.client_conn.send(
                                        {
                                            'mac_addr': address,
                                            'electrode_voltage':list(data)
                                        }
                                    )

                                await client.start_notify(FEEDBACK_CHAR, notification_handler)

                                print("send_then_read:CONNECTED", client)

                                if SERIAL_COMMAND_INPUT_CHAR in data:
                                    print("send_then_read:SERIAL COMMAND INPUT")
                                    k = SERIAL_COMMAND_INPUT_CHAR
                                    for v in data[k]:
                                        print("send_then_read:sending", v)
                                        await client.write_gatt_char(k, str(v).encode('utf-8'), False)
                                        await asyncio.sleep(0.05, loop=loop)

                                await client.stop_notify(FEEDBACK_CHAR)

                            return client
                    print("send_then_read:NOT CONNECTED")
                    return None
        except BleakError as e:
            print("send_then_read:BLEAK ERROR", e)
        if depth < 5:
            depth = depth + 1
            await asyncio.sleep(depth, loop=loop)
            print("send_then_read:SEND AGAIN")
            return await self.send(address, loop, data, depth)
        return None

    def r(self, msg):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(1)
        loop.run_until_complete(self.stream(msg, loop))

    def s(self, address, data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(1)
        loop.run_until_complete(self.send(address, loop, data))

    def s_t_r(self, address, data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(1)
        loop.run_until_complete(self.send_then_read(address, loop, data))

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

                    print("send", send)
                    print("read", read)

                    if send and not read:

                        address = msg.pop('mac_addr')

                        data = msg
                        t = threading.Thread(target=self.s, args=(address, data))
                        t.start()

                        # time.sleep(40)
                        # t = threading.Thread(target=self.r, args=(address,))
                        # t.start()
                    elif send and read:

                        address = msg.pop('mac_addr')

                        data = msg
                        t = threading.Thread(target=self.s_t_r, args=(address, data))
                        t.start()

            listener.close()
        except Exception as e:
            print(e)

    def ble_discover_loop(self):
        try:
            time = 0.5
            self.client_address = ('localhost', 6000)
            self.client_conn = Client(self.client_address, authkey=b'password')
            while True:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.set_debug(1)
                r1 = loop.run_until_complete(self.ble_discover(loop, time))
                devices = r1.result()

                if self.prune:
                    # for i in devices:
                    #     print(i)
                    data = [{'text': str(i.address)} for i in devices if
                            i.address is not None and "Neuro" in str(i)]
                else:
                    data = [{'text': str(i.address)} for i in devices if i.address is not None]
                if time < 10:
                    time += 1
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
