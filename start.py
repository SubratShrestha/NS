import time
import subprocess

"""
This file is used as the main application to start the UI and then the BLE before closing them and killing the processes.
Compiled with PyInstaller on Windows.
"""

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
