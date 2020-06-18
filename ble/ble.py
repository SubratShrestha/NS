from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
import asyncio
import threading
from multiprocessing.connection import Listener, Client
import sys

async def ble_discover(loop, time):
    task1 = loop.create_task(discover(time))
    await asyncio.wait([task1])
    return task1

def BluetoothDiscoverLoop():
    try:
        time = 0.5
        client_address = ('localhost', 6000)
        conn = Client(client_address, authkey=b'password')
        while True:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.set_debug(1)
            r1 = loop.run_until_complete(ble_discover(loop, time))
            devices = r1.result()

            prune = len(sys.argv) > 1 and "-prune" in sys.argv
            if prune:
                data = [{'text': str(i.address)} for i in devices if i.address is not None and "NeuroStimulator" in str(i)]
            else:
                data = [{'text': str(i.address)} for i in devices if i.address is not None]
            if time < 10:
                time += 1
            if conn.closed:
                break
            else:
                conn.send(data)
                print(data)
    except Exception as e:
        print(e)
    finally:
        try:
            conn.close()
        except UnboundLocalError as e:
            print(e)


async def connect(address, loop):
    async with BleakClient(address, loop=loop) as client:
        try:
            await client.connect()
            return client
        except Exception as e:
            print(e)
        except BleakDotNetTaskError as e:
            print(e)
        except BleakError as e:
            print(e)
        finally:
            if await client.is_connected():
                print("CONNECTED")
                return client
            return None

if __name__ == '__main__':
    t = threading.Thread(target=BluetoothDiscoverLoop)
    t.start()
