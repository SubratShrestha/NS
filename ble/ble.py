from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
import asyncio
import threading
from multiprocessing.connection import Listener, Client
import sys
import ast

BATTERY_LEVEL_CHAR = '00002a19-0000-1000-8000-00805f9b34fb'
CHANNEL_NUM_CHAR = '01000000-0000-0000-0000-000000000006'
MAX_FREQ_CHAR = '01000000-0000-0000-0000-000000000007'
OTA_SUPPORT_CHAR = '01000000-0000-0000-0000-000000000008'

RAMP_UP_WRITE_CHAR = '02000000-0000-0000-0000-00000000010d'
SHORT_ELECTRODE_WRITE_CHAR = '02000000-0000-0000-0000-00000000010e'
PHASE_ONE_WRITE_CHAR = '02000000-0000-0000-0000-000000000103'
PHASE_TWO_WRITE_CHAR = '02000000-0000-0000-0000-000000000105'
STIM_AMP_WRITE_CHAR = '02000000-0000-0000-0000-000000000102'
INTER_PHASE_GAP_WRITE_CHAR = '02000000-0000-0000-0000-000000000104'
INTER_STIM_DELAY_WRITE_CHAR = '02000000-0000-0000-0000-000000000106'
PULSE_NUM_WRITE_CHAR = '02000000-0000-0000-0000-000000000107'
ANODIC_CATHOLIC_FIRST_WRITE_CHAR = '02000000-0000-0000-0000-000000000108'
STIM_TYPE_WRITE_CHAR = '02000000-0000-0000-0000-000000000109'
BURST_NUM_WRITE_CHAR = '02000000-0000-0000-0000-00000000010a'
INTER_BURST_DELAY_WRITE_CHAR = '02000000-0000-0000-0000-00000000010b'
SERIAL_COMMAND_INPUT_CHAR = '02000000-0000-0000-0000-000000000101'

RAMP_UP_READ_CHAR = '02000000-0000-0000-0000-00000000000d'
SHORT_ELECTRODE_READ_CHAR = '02000000-0000-0000-0000-00000000000e'
INTER_PHASE_GAP_READ_CHAR = '02000000-0000-0000-0000-000000000004'
PHASE_ONE_READ_CHAR = '02000000-0000-0000-0000-000000000003'
PHASE_TWO_READ_CHAR = '02000000-0000-0000-0000-000000000005'
STIM_AMP_READ_CHAR = '02000000-0000-0000-0000-000000000002'
INTER_STIM_DELAY_READ_CHAR = '02000000-0000-0000-0000-000000000006'
PULSE_NUM_READ_CHAR = '02000000-0000-0000-0000-000000000007'
ANODIC_CATHODIC_FIRST_READ_CHAR = '02000000-0000-0000-0000-000000000008'
STIM_TYPE_READ_CHAR = '02000000-0000-0000-0000-000000000009'
BURST_NUM_READ_CHAR = '02000000-0000-0000-0000-00000000000a'
INTER_BURST_DELAY_READ_CHAR = '02000000-0000-0000-0000-00000000000b'

class BluetoothComms():
    def __init__(self):
        self.prune = len(sys.argv) > 1 and "-prune" in sys.argv
        self.thread = True
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.receive_thread.start()
        self.discover_thread = threading.Thread(target=self.ble_discover_loop)
        self.discover_thread.start()
        self.connected = {}

        self.readable_chars = [
            INTER_PHASE_GAP_READ_CHAR,
            PHASE_ONE_READ_CHAR,
            PHASE_TWO_READ_CHAR,
            STIM_AMP_READ_CHAR,
            INTER_STIM_DELAY_READ_CHAR,
            PULSE_NUM_READ_CHAR,
            ANODIC_CATHODIC_FIRST_READ_CHAR,
            STIM_TYPE_READ_CHAR,
            BURST_NUM_READ_CHAR,
            INTER_BURST_DELAY_READ_CHAR,
            CHANNEL_NUM_CHAR,
            MAX_FREQ_CHAR,
            OTA_SUPPORT_CHAR,
            BATTERY_LEVEL_CHAR,
            RAMP_UP_READ_CHAR,
            SHORT_ELECTRODE_READ_CHAR
        ]

        self.char_to_string_mapping = {
            INTER_PHASE_GAP_READ_CHAR:'INTER_PHASE_GAP_READ_CHAR',
            PHASE_ONE_READ_CHAR:'PHASE_ONE_READ_CHAR',
            PHASE_TWO_READ_CHAR:'PHASE_TWO_READ_CHAR',
            STIM_AMP_READ_CHAR:'STIM_AMP_READ_CHAR',
            INTER_STIM_DELAY_READ_CHAR:'INTER_STIM_DELAY_READ_CHAR',
            PULSE_NUM_READ_CHAR:'PULSE_NUM_READ_CHAR',
            ANODIC_CATHODIC_FIRST_READ_CHAR:'ANODIC_CATHODIC_FIRST_READ_CHAR',
            STIM_TYPE_READ_CHAR:'STIM_TYPE_READ_CHAR',
            BURST_NUM_READ_CHAR:'BURST_NUM_READ_CHAR',
            INTER_BURST_DELAY_READ_CHAR:'INTER_BURST_DELAY_READ_CHAR',
            CHANNEL_NUM_CHAR:'CHANNEL_NUM_CHAR',
            MAX_FREQ_CHAR:'MAX_FREQ_CHAR',
            OTA_SUPPORT_CHAR:'OTA_SUPPORT_CHAR',
            BATTERY_LEVEL_CHAR:'BATTERY_LEVEL_CHAR',
            RAMP_UP_READ_CHAR:'RAMP_UP_READ_CHAR',
            SHORT_ELECTRODE_READ_CHAR:'SHORT_ELECTRODE_READ_CHAR'
        }

        self.writeable_chars = [
            PHASE_ONE_WRITE_CHAR,
            PHASE_TWO_WRITE_CHAR,
            STIM_AMP_WRITE_CHAR,
            INTER_PHASE_GAP_WRITE_CHAR,
            INTER_STIM_DELAY_WRITE_CHAR,
            PULSE_NUM_WRITE_CHAR,
            ANODIC_CATHOLIC_FIRST_WRITE_CHAR,
            STIM_TYPE_WRITE_CHAR,
            BURST_NUM_WRITE_CHAR,
            INTER_BURST_DELAY_WRITE_CHAR,
            SERIAL_COMMAND_INPUT_CHAR,
            SHORT_ELECTRODE_WRITE_CHAR,
            RAMP_UP_WRITE_CHAR
        ]

        self.write_to_read = {
            PHASE_ONE_WRITE_CHAR:PHASE_ONE_READ_CHAR,
            PHASE_TWO_WRITE_CHAR:PHASE_TWO_READ_CHAR,
            STIM_AMP_WRITE_CHAR:STIM_AMP_READ_CHAR,
            INTER_PHASE_GAP_WRITE_CHAR:INTER_PHASE_GAP_READ_CHAR,
            INTER_STIM_DELAY_WRITE_CHAR:INTER_STIM_DELAY_READ_CHAR,
            PULSE_NUM_WRITE_CHAR:PULSE_NUM_READ_CHAR,
            ANODIC_CATHOLIC_FIRST_WRITE_CHAR:ANODIC_CATHODIC_FIRST_READ_CHAR,
            STIM_TYPE_WRITE_CHAR:STIM_TYPE_READ_CHAR,
            BURST_NUM_WRITE_CHAR:BURST_NUM_READ_CHAR,
            INTER_BURST_DELAY_WRITE_CHAR:INTER_BURST_DELAY_READ_CHAR,
            SERIAL_COMMAND_INPUT_CHAR:SERIAL_COMMAND_INPUT_CHAR,
            SHORT_ELECTRODE_WRITE_CHAR:SHORT_ELECTRODE_READ_CHAR,
            RAMP_UP_WRITE_CHAR:RAMP_UP_READ_CHAR
        }


    async def ble_discover(self, loop, time):
        task1 = loop.create_task(discover(time))
        await asyncio.wait([task1])
        return task1

    def notification_handler(self, sender, data):
        """Simple notification handler which prints the data received."""
        print("{0}: {1}".format(sender, data))

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
                        print("CONNECTED", client)
                        if SERIAL_COMMAND_INPUT_CHAR in data:
                            k = SERIAL_COMMAND_INPUT_CHAR
                            for v in data[k]:
                                print(v)
                                await client.write_gatt_char(k, str(v).encode('utf-8'), True)
                                await asyncio.sleep(0.1, loop=loop)
                        else:
                            for k,v in data.items():
                                print(v)
                                await client.write_gatt_char(k, str(v).encode('utf-8'), True)
                                await asyncio.sleep(0.1, loop=loop)
                        return client
                    print("NOT CONNECTED")
                    return None
        except BleakError as e:
            print("BLEAK ERROR", e)
        if depth < 3:
            depth = depth + 1
            await self.send(address, loop, data, depth)

    async def read(self, address, loop):
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
                        services = await client.get_services()
                        services = vars(services)
                        data = {}
                        for k, v in services.items():
                            if 'characteristics' in k:
                                for sk, sv in v.items():
                                    sv = str(sv).replace(':', "").replace(' ', "")
                                    if sv in self.readable_chars:
                                        result = await client.read_gatt_char(sv)
                                        await asyncio.sleep(0.1, loop=loop)
                                        if sv == BATTERY_LEVEL_CHAR:
                                            result = str(int(result.hex(), 16))
                                        else:
                                            result = result.decode("utf-8")
                                        data[self.char_to_string_mapping[sv]] = result
                        data['mac_addr'] = address
                        self.client_conn.send(data)
                        return client
                    print("NOT CONNECTED")
                    return None
        except BleakError as e:
            print("BLEAK ERROR", e)

    def receive_loop(self):
        try:
            address = ('localhost', 6001)
            listener = Listener(address, authkey=b'password')
            conn = listener.accept()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.set_debug(1)
            while self.thread:
                msg = conn.recv()
                print("receive_loop->", msg)
                if isinstance(msg, str):
                    print("run read until complete")
                    loop.run_until_complete(self.read(msg, loop))
                    print("completed running read")
                else:
                    address = msg.pop('mac_addr')
                    print("sending to: ", address)
                    data = msg
                    loop.run_until_complete(self.send(address, loop, data))
                    print("finished self.send")
                loop.close()
                asyncio.set_event_loop(None)
            listener.close()
        except Exception as e:
            print(e)

    async def write_char(self, mac_addr: str, loop: asyncio.AbstractEventLoop, uuid: str, value: str):
        data = {str(uuid): str(value)}
        await self.send(mac_addr, loop, data)

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
                    data = [{'text': str(i.address)} for i in devices if
                            i.address is not None and "NeuroStimulator" in str(i)]
                else:
                    data = [{'text': str(i.address)} for i in devices if i.address is not None]
                if time < 10:
                    time += 1
                if self.client_conn.closed:
                    break
                else:
                    self.client_conn.send(data)
                    for i in data:
                        print(i)
                loop.close()
                asyncio.set_event_loop(None)
        except Exception as e:
            print(e)
        finally:
            try:
                self.client_conn.close()
            except UnboundLocalError as e:
                print(e)

if __name__ == '__main__':
    ble_comms = BluetoothComms()