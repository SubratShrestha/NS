import kivy
kivy.require("1.10.0")
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.recycleview import RecycleView
from kivy.base import runTouchApp
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
import json
import serial
import asyncio
from bleak import discover, BleakClient, BleakScanner
from scipy import signal
import matplotlib.pyplot as plt

"""
Currently used Libraries:
    - kivy:
        - documentation: https://kivy.org/doc/stable/
        - starter tutorial: https://www.youtube.com/watch?v=GXP8O4dSS3E
    - bleak:
        -documentation: https://bleak.readthedocs.io/en/latest/

Future Libraries which are expected to be useful:
    - json:
        - documentation: https://docs.python.org/3/library/json.html
    - serial:
        - documentation: https://pythonhosted.org/pyserial/
    - scipy:
        - square signal:
            - documentation: https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.square.html
"""

MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
"""
The connect function tries to connect to the given bluetooth address asynchronously.
It then tries to read the device model_number and print it out.
If it fails, it just prints out the error currently.
"""
async def connect(address, loop):
    async with BleakClient(address, loop=loop) as client:
        try:
            await client.connect()
            model_number = await client.read_gatt_char(MODEL_NBR_UUID)
            print("Model Number: {0}".format("".join(map(chr, model_number))))
        except Exception as e:
            print(e)
        finally:
            await client.disconnect()

async def scan(app):
    scanner = BleakScanner()
    scanner.register_detection_callback(app.scan_callback())
    await scanner.start()
    await asyncio.sleep(5.0)
    await scanner.stop()
    devices = await scanner.get_discovered_devices()
    for i in devices:
        print(i)

"""
This is the invisible wrapper which takes place over all items in the recyclerview.
For more information search kivy FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
"""
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

"""
This is the individual selectable label which populates the SelectableRecycleBoxLayout in the bluetooth recyclerview.
It is defined on the app.kv file.
"""
class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None # this is the index of the label in the recyclerview
    selected = BooleanProperty(False) # true if selected, false otherwise
    selectable = BooleanProperty(True) # permissions as to whether it is selectable

    def refresh_view_attrs(self, rv, index, data):
        '''
        Catch and handle the view changes
        Update the index, then use the super class to call the same function
        '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        '''
        This function just returns true or false if the label was clicked or touched.
        '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        '''
        This is called if a label is selected.

        Change the selected value.
        '''
        self.selected = is_selected
        if is_selected:
            """The label was selected, therefore we print this label's data"""
            print("selection changed to {0}".format(rv.data[index]))
            """
            event loops are asynchronous tasks/callbacks
            get_event_loop() returns the running event loop
            """
            loop = asyncio.get_event_loop()
            """
            Split the label's text is such a way that the ble address is retrieved.
            Then use try to connect to the ble address asynchronously.
            """
            ble_address = rv.data[index]['text'].split(': ')[0]
            loop.run_until_complete(connect(ble_address,loop))
        else:
            """
            The label was not selected or was just deselected.
            """
            print("selection removed for {0}".format(rv.data[index]))

"""
This is the bluetooth recyclerview, as defined in the app.kv file.
It has all the functionality of a recycleview component.
self.data is a list which is meant to contain a dictionary ble devices.
"""
class BLE_RV(RecycleView):
    def __init__(self, **kwargs):
        super(BLE_RV, self).__init__(**kwargs)
        self.data = []

"""
This class is the main window which contains all other components, as defined in the app.kv file.

The components are referenceable via their id.
An example of this is the self.ble_rv, which references the recycler view.
Note that self.ble_rv is not created in python, but rather in app.kv.
"""
class NS_Window(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.devices = []
    """This function discovers bluetooth devices and then adds the them to the recycler view's data"""
    async def ble_discover(self):
        """Discover the devices, may take a few seconds"""
        self.devices = await discover()
        """Add them to the recycler data section as a list of dictionarys'"""
        self.ble_rv.data = [{'text':str(i)} for i in self.devices]

    def scan_callback(*args):
        print(args)


    """This function is called when the discover bluetooth button is clicked"""
    def connect_to_bluetooth(self):
        """
        event loops are asynchronous tasks/callbacks
        get_event_loop() returns the running event loop
        """
        loop = asyncio.get_event_loop()
        """
        Run the asynchronous function self.ble_discover() until it's finished
        """
        loop.run_until_complete(self.ble_discover())


"""Define the App, which in this case is just the NS_Window currently"""
class App(App):
    def build(self):
        return NS_Window()

if __name__ == '__main__':
    """Create the App and Run"""
    App = App()
    App.run()
    scan(App)
