from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
import asyncio

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

async def send(address, data, depth=0):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
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
                        for k, v in data.items():
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
        await send(address, loop, data, depth)

