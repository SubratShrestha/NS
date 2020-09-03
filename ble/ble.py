from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
import asyncio
import threading
from multiprocessing.connection import Listener, Client
import sys
import ast

if '-esp' in sys.argv:
    SERIAL_COMMAND_INPUT_CHAR = '02000000-0000-0000-0000-000000000101'
elif '-stm' in sys.argv:
    SERIAL_COMMAND_INPUT_CHAR = '0000fe41-8e22-4541-9d4c-21edae82ed19'
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

    def notification_handler(self, sender, data):
        """Simple notification handler which prints the data received."""
        print("{0}: {1}".format(sender, list(data)))

    async def stream(self, address, loop, depth=0):
        print("SEND")
        try:
            async with BleakClient(address, loop=loop) as client:
                try:
                    print("TRY TO CONNECT")
                    await client.connect(timeout=10)
                except Exception as e:
                    print("Exception", e)
                except BleakDotNetTaskError as e:
                    print("BleakDotNetTaskError", e)
                except BleakError as e:
                    print("BleakError", e)
                finally:
                    if await client.is_connected():

                        try:
                            print("TRY TO CONNECT")
                            await client.connect(timeout=10)
                        except Exception as e:
                            print("Exception", e)
                        except BleakDotNetTaskError as e:
                            print("BleakDotNetTaskError", e)
                        except BleakError as e:
                            print("BleakError", e)
                        finally:
                            if await client.is_connected():
                                print("NOTIFICATIONS FOR STREAMING")
                                await client.start_notify(STREAM_READ_CHAR, self.notification_handler)
                                await asyncio.sleep(30.0, loop=loop)
                                await client.stop_notify(STREAM_READ_CHAR)
                            return client
                    print("NOT CONNECTED")
                    return None
        except BleakError as e:
            print("BLEAK ERROR", e)
        if depth < 3:
            depth = depth + 1
            print("SEND AGAIN")
            return await self.stream(address, loop, depth)
        return None

    async def send(self, address, loop, data, depth=0):
        print("SEND")
        try:
            async with BleakClient(address, loop=loop) as client:
                try:
                    print("TRY TO CONNECT")
                    await client.connect(timeout=10)
                except Exception as e:
                    print("Exception", e)
                except BleakDotNetTaskError as e:
                    print("BleakDotNetTaskError", e)
                except BleakError as e:
                    print("BleakError", e)
                finally:
                    if await client.is_connected():

                        try:
                            print("TRY TO CONNECT")
                            await client.connect(timeout=10)
                        except Exception as e:
                            print("Exception", e)
                        except BleakDotNetTaskError as e:
                            print("BleakDotNetTaskError", e)
                        except BleakError as e:
                            print("BleakError", e)
                        finally:
                            if await client.is_connected():
                                services = await client.get_services()
                                services = vars(services)
                                for k, v in services.items():
                                    # print("services",k,v)
                                    if 'characteristics' in k:
                                        # print(len(v.keys()))
                                        for sk, sv in v.items():
                                            print(sv)
                                            if sv == SERIAL_COMMAND_INPUT_CHAR:
                                                print("SERIAL INPUT COMMAND FOUND")
                                            await asyncio.sleep(1, loop=loop)

                                print("CONNECTED", client)
                                if SERIAL_COMMAND_INPUT_CHAR in data:
                                    print("SERIAL COMMAND INPUT")
                                    k = SERIAL_COMMAND_INPUT_CHAR
                                    for v in data[k]:
                                        print("sending", v)
                                        await client.write_gatt_char(k, str(v).encode('utf-8'), False)
                                        await asyncio.sleep(1, loop=loop)
                                else:
                                    for k,v in data.items():
                                        print(v)
                                        await client.write_gatt_char(k, str(v).encode('utf-8'), False)
                                        await asyncio.sleep(1, loop=loop)
                            return client
                    print("NOT CONNECTED")
                    return None
        except BleakError as e:
            print("BLEAK ERROR", e)
        if depth < 3:
            depth = depth + 1
            print("SEND AGAIN")
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
        result = loop.run_until_complete(self.send(address, loop, data))
        print("s result",result)

    def receive_loop(self):
        try:
            address = ('localhost', 6001)
            listener = Listener(address, authkey=b'password')
            conn = listener.accept()
            # loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(loop)
            # loop.set_debug(1)
            while self.thread:
                msg = conn.recv()
                if isinstance(msg, str):
                    t = threading.Thread(target=self.r, args=(msg,))
                    t.start()
                else:
                    address = msg.pop('mac_addr')
                    data = msg
                    t = threading.Thread(target=self.s, args=(address, data))
                    t.start()

                    t = threading.Thread(target=self.r, args=(address,))
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
        finally:
            try:
                self.client_conn.close()
            except UnboundLocalError as e:
                print(e)

if __name__ == '__main__':
    ble_comms = BluetoothComms()