import pygatt
import re
import tkinter as tk
from functools import partial

def call_result(label_result, n1):
    num1 = str(n1.get())
    label_result.config(text="Comport is %s" % num1)
    adapter = pygatt.BGAPIBackend(serial_port=str(num1))
    adapter.start()
    listOfDevices = adapter.scan()
    print (listOfDevices)
    return

root = tk.Tk()
root.geometry('800x400+100+200')
root.title('Project')
number1 = tk.StringVar()
labelTitle = tk.Label(root, text="Project").grid(row=0, column=2)
labelNum1 = tk.Label(root, text="Enter Comport of dongle").grid(row=1, column=0)
labelResult = tk.Label(root)
labelResult.grid(row=7, column=2)
entryNum1 = tk.Entry(root, textvariable=number1).grid(row=1, column=2)
call_result = partial(call_result, labelResult, number1)
buttonCal = tk.Button(root, text="Get ComPort", command=call_result).grid(row=3, column=0)

root.mainloop()