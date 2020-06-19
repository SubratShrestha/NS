import asyncio
import platform

from bleak import BleakClient


async def print_services(mac_addr: str, loop: asyncio.AbstractEventLoop):
    async with BleakClient(mac_addr, loop=loop) as client:
        svcs = await client.get_services()
        print("Services:", svcs)


mac_addr = ("C8:2B:96:A2:85:F6")
loop = asyncio.get_event_loop()
loop.run_until_complete(print_services(mac_addr, loop))