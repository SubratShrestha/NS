import kivy
from bleak.exc import BleakDotNetTaskError, BleakError
from kivy.app import App
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
import asyncio
from bleak import discover, BleakClient, BleakScanner
import json
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

devices_dict = {}

def get_squarewave_plot():
    t = np.linspace(0, 1, 500, endpoint=False)
    plt.plot(t, signal.square(2 * np.pi * 5 * t))
    plt.ylim(-2, 2)
    # plt.figure()
    return FigureCanvasKivyAgg(plt.gcf())

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

class ScreenManagement(ScreenManager):
    pass

class DeviceScreen(Screen):
    pass

class AddDevicePopup(Popup):
    async def ble_discover(self):
        self.devices = await discover()
        self.ble_rv.data = [{'text': str(i.address)} for i in self.devices if i.address is not None]

    def BluetoothDiscoverLoop(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.ble_discover())

    def Close(self):
        # print(devices_dict)
        data = App.get_running_app().root.current_screen.device_rv.data

        for j in devices_dict.keys():
            adding = True
            for i in data:
                if i['text'] == j:
                    adding = False
            if adding and devices_dict[j]:
                App.get_running_app().root.current_screen.device_rv.data.append({'text': j})
        print(App.get_running_app().root.current_screen.device_rv.data)
        self.dismiss()

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.devices = []

    def save_input_data(self):
        print(self.input_amplitude.text)
        print(self.input_frequency.text)
        print(self.input_pulse_width.text)
        print(self.input_interstim_delay.text)
        msg = json.dumps({
            "amplitude":str(self.input_amplitude.text) if self.input_amplitude.text else "",
            "frequency":str(self.input_frequency.text) if self.input_frequency.text else "",
            "pulse_width":str(self.input_pulse_width.text) if self.input_pulse_width.text else "",
            "interstim_delay":str(self.input_interstim_delay.text) if self.input_interstim_delay.text else ""
        })
        print(msg)
        self.grid_plot.add_widget(get_squarewave_plot())

class DeviceTabs(TabbedPanel):
    pass

class PhaseTimeFrequencyTabs(TabbedPanel):
    pass

class BurstUniformStimulationTabs(TabbedPanel):
    pass

class TerminationTabs(TabbedPanel):
    pass

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class AddDeviceSelectableLabel(RecycleDataViewBehavior, Label):
    index = None  # this is the index of the label in the recyclerview
    selected = BooleanProperty(False)  # true if selected, false otherwise
    selectable = BooleanProperty(True)  # permissions as to whether it is selectable

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(AddDeviceSelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(AddDeviceSelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

        if rv.data[index]['text'] in devices_dict:
            devices_dict[rv.data[index]['text']] = is_selected

        if is_selected and rv.data[index]['text'] not in devices_dict:
            # rv.parent.parent.parent.parent.dismiss()
            devices_dict[rv.data[index]['text']] = True
            # loop = asyncio.get_event_loop()
            # client = loop.run_until_complete(connect(rv.data[index]['text'],loop))
            # if client is not None:
            #     print("CLIENT OBJ RETURNED")

class ConnectedDeviceSelectableLabel(RecycleDataViewBehavior, Label):
    index = None  # this is the index of the label in the recyclerview
    selected = BooleanProperty(False)  # true if selected, false otherwise
    selectable = BooleanProperty(True)  # permissions as to whether it is selectable

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(ConnectedDeviceSelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(ConnectedDeviceSelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        if is_selected and not self.selected:
            self.selected = is_selected
            print("Device")
            App.get_running_app().root.current = 'device'
            App.get_running_app().root.current_screen.device_rv.data = rv.data
        elif is_selected and self.selected:
            self.selected = not is_selected
            print("Home")
            App.get_running_app().root.current = 'home'
            App.get_running_app().root.current_screen.device_rv.data = rv.data

class NeuroStimApp(App):
    def __init__(self, kvloader):
        super(NeuroStimApp, self).__init__()
        self.kvloader = kvloader

    def build(self):
        return self.kvloader

if __name__ == '__main__':
    # Window.fullscreen = True
    kvloader = Builder.load_file("ui.kv")
    App = NeuroStimApp(kvloader)
    App.run()
