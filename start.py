import time
import subprocess

print("run ui")
ui = subprocess.Popen([".\\windows_pygatt.exe"])

print("sleep")
time.sleep(3)

print("run ble")
ble = subprocess.Popen([".\\pygatt_ble_windows.exe"])

print("running")
ui.wait()
ble.kill()

print("closed")
