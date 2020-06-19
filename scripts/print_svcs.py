import asyncio

from bleak import discover, BleakClient
from bleak.exc import BleakDotNetTaskError, BleakError

DEVICE_INFO_SERVICE               = '180A'
MANUFACTURER_NAME_CHAR            = '2A29'
HARDWARE_REVISION_CHAR            = '2A27'
FIRMWARE_REVISION_CHAR            = '2A26'
SOFTWARE_REVISION_CHAR            = '2A28'
BATTRY_SERVICE                    = '180F'
BATTRY_LEVEL_CHAR                 = '2A19'

CHANNEL_NUM_CHAR                  =  '01000000-0000-0000-0000-000000000006'
MAX_FREQ_CHAR                     =  '01000000-0000-0000-0000-000000000007'
OTA_SUPPORT_CHAR                  =  '01000000-0000-0000-0000-000000000008'
STIMULATION_COMMAND_SERVICE       =  '02000000-0000-0000-0000-000000000001'
STIM_AMP_READ_CHAR                =  '02000000-0000-0000-0000-000000000002'
STIM_AMP_WRITE_CHAR               =  '02000000-0000-0000-0000-000000000102'
PHASE_ONE_READ_CHAR               =  '02000000-0000-0000-0000-000000000003'
PHASE_ONE_WRITE_CHAR              =  '02000000-0000-0000-0000-000000000103'
INTER_PHASE_GAP_READ_CHAR         =  '02000000-0000-0000-0000-000000000004'
INTER_PHASE_GAP_WRITE_CHAR        =  '02000000-0000-0000-0000-000000000104'
PHASE_TWO_READ_CHAR               =  '02000000-0000-0000-0000-000000000005'
PHASE_TWO_WRITE_CHAR              =  '02000000-0000-0000-0000-000000000105'
INTER_STIM_DELAY_READ_CHAR        =  '02000000-0000-0000-0000-000000000006'
INTER_STIM_DELAY_WRITE_CHAR       =  '02000000-0000-0000-0000-000000000106'
STIMULATION_DURATION_READ_CHAR    =  '02000000-0000-0000-0000-000000000007'
STIMULATION_DURATION_WRITE_CHAR   =  '02000000-0000-0000-0000-000000000107'
ANODIC_CATHODIC_FIRST_READ_CHAR   =  '02000000-0000-0000-0000-000000000008'
ANODIC_CATHODIC_FIRST_WRITE_CHAR  =  '02000000-0000-0000-0000-000000000108'
STIM_TYPE_READ_CHAR               =  '02000000-0000-0000-0000-000000000009'
STIM_TYPE_WRITE_CHAR              =  '02000000-0000-0000-0000-000000000109'
BURST_TIME_READ_CHAR              =  '02000000-0000-0000-0000-00000000000A'
BURST_TIME_WRITE_CHAR             =  '02000000-0000-0000-0000-00000000010A'
INTER_BURST_DELAY_READ_CHAR       =  '02000000-0000-0000-0000-00000000000B'
INTER_BURST_DELAY_WRITE_CHAR      =  '02000000-0000-0000-0000-00000000010B'

readable_chars = [
    STIM_AMP_READ_CHAR,
    PHASE_ONE_READ_CHAR,
    INTER_PHASE_GAP_READ_CHAR,
    PHASE_TWO_READ_CHAR,
    INTER_STIM_DELAY_READ_CHAR,
    STIMULATION_DURATION_READ_CHAR,
    ANODIC_CATHODIC_FIRST_READ_CHAR,
    STIM_TYPE_READ_CHAR,
    BURST_TIME_READ_CHAR,
    INTER_BURST_DELAY_READ_CHAR
]

writeable_chars = [
    STIM_AMP_WRITE_CHAR,
    PHASE_ONE_WRITE_CHAR,
    INTER_PHASE_GAP_WRITE_CHAR,
    PHASE_TWO_WRITE_CHAR,
    INTER_STIM_DELAY_WRITE_CHAR,
    STIMULATION_DURATION_WRITE_CHAR,
    ANODIC_CATHODIC_FIRST_WRITE_CHAR,
    STIM_TYPE_WRITE_CHAR,
    BURST_TIME_WRITE_CHAR,
    INTER_BURST_DELAY_WRITE_CHAR
]

async def connect(address, loop):
    async with BleakClient(address, loop=loop) as client:
        print("Try Connecting")
        try:
            await client.connect()
        except Exception as e:
            print(e)
        except BleakDotNetTaskError as e:
            print(e)
        except BleakError as e:
            print(e)
        finally:
            if await client.is_connected():
                print("CONNECTED")
                services = await client.get_services()
                svs = vars(services)
                tes = services.get_service(STIMULATION_COMMAND_SERVICE)
                print(tes)
                for k,v in svs.items():
                    if 'services' in k:
                        print(k)
                        print(v)
                        print("=================== Services ==================")
                        for sk,sv in v.items():
                            # print(sv)
                            # print(sk)
                            print(services.get_service(sk))
                        print("\n===============================================\n\n")
                    if 'characteristics' in k:
                        print("=================== characteristics ==================")
                        for sk,sv in v.items():
                            print(sk)
                            if sk in readable_chars:
                                print(await client.read_gatt_char(sk))
                            if sk in writeable_chars:
                                print(await client.write_gatt_char(sk, bytearray(b'0'), True))
                        print("===============================================\n\n")
                    #
                    if 'descript' in k:
                        print("=================== descript ==================")
                        for sk,sv in v.items():
                            print(sk)
                            print(await client.read_gatt_descriptor(sk))
                    #     print("===============================================\n\n")

                print(await client.disconnect())
                return client

async def ble_discover(loop, time):
    task1 = loop.create_task(discover(time))
    await asyncio.wait([task1])
    return task1

async def ble_print_connection(loop,d):
    task1 = loop.create_task(connect(d, loop))
    await asyncio.wait([task1])
    return task1

def BluetoothDiscoverLoop():
    loop = asyncio.get_event_loop()
    client = loop.run_until_complete(connect('C8:2B:96:A2:85:F6', loop))
    # print("RETURNED")
    # if client is not None:
    #     print("CLIENT OBJ RETURNED")

if __name__ == '__main__':
    BluetoothDiscoverLoop()