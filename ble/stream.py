loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.set_debug(1)
loop.run_until_complete(self.send(address, loop, data))
async with BleakClient(address='80:E1:26:08:05:56', loop=loop) as client:
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


            # stop_event = asyncio.Event()

            def notification_handler(sender, data):
                """Simple notification handler which prints the data received."""
                # print("Notifictation Stream {0}: {1}".format(sender, list(data)))
                # loop.call_soon_threadsafe(stop_event.set)
                print("NOTIFICATION")


            await client.start_notify(STREAM_READ_CHAR, notification_handler)

            # while True:
            # if not await client.is_connected():
            #     await client.connect(timeout=10)
            #     continue
            # await stop_event.wait()
            await asyncio.sleep(120, loop=loop)

            await client.stop_notify(STREAM_READ_CHAR)

            print("END STREAM")


