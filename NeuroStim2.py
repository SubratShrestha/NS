from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
from kivy.uix.popup import Popup
import asyncio

devices_dict = {}

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


class MainWindow(BoxLayout):
    pass


class SideBar(FloatLayout):
    pass


class ScreenManagement(ScreenManager):
    pass


class HomeScreen(Screen):
    pass


class DeviceScreen(Screen):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class AddDevicePopup(Popup):
    async def ble_discover(self):
        self.devices = await discover()
        self.ble_rv.data = [{'text': str(i.address)} for i in self.devices if i.address is not None]

    def BluetoothDiscoverLoop(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.ble_discover())

    def Close(self):
        data = App.get_running_app().root.device_rv.data

        for j in devices_dict.keys():
            adding = True
            for i in data:
                if i['text'] == j:
                    adding = False
            if adding and devices_dict[j]:
                App.get_running_app().root.device_rv.data.append({'text': j})
        print(App.get_running_app().root.device_rv.data)
        self.dismiss()


class AddDeviceSelectableLabel(RecycleDataViewBehavior,Label):
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


class NeuroStimApp(App):
    def __init__(self, kvloader):
        super(NeuroStimApp, self).__init__()
        self.kvloader = kvloader

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    kvloader = Builder.load_file("ui2.kv")
    App = NeuroStimApp(kvloader)
    App.run()
