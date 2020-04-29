from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
import asyncio
from bleak import discover


class NeuroStimMainWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.devices = []

    async def ble_discover(self):
        self.devices = await discover()
        self.ble_rv.data = [{'text': str(i)} for i in self.devices]

    def BluetoothDiscoverLoop(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.ble_discover())


class BluetoothDiscoverRV(RecycleView):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None  # this is the index of the label in the recyclerview
    selected = BooleanProperty(False)  # true if selected, false otherwise
    selectable = BooleanProperty(True)  # permissions as to whether it is selectable

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected


class NeuroStimBluetoothWindow(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


kvloader = Builder.load_file("UI_Framework.kv")


class NeuroStimApp(App):
    def build(self):
        return kvloader


if __name__ == '__main__':
    NeuroStimApp().run()
