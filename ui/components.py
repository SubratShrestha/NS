from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelStrip
from kivy.uix.textinput import TextInput
import re

from consts import UINT32_MAX


class NumericInput(TextInput):
    def __init__(self, *args, **kwargs):
        super(NumericInput, self).__init__(*args, **kwargs)
        self.min = 0
        self.max = UINT32_MAX

    def insert_text(self, string, from_undo=False):
        new_text = self.text + string
        new_text = re.sub("[^0-9]", "", new_text)
        if new_text != "":
            if self.min <= float(new_text) <= self.max:
                super(NumericInput, self).insert_text(string, from_undo=from_undo)

class DT_TPS(TabbedPanelStrip):
    pass


class DeviceTabs(TabbedPanel, DT_TPS):
    def __init__(self, **kargs):
        super(DeviceTabs, self).__init__(**kargs)
        self._tab_layout.padding = '2dp', '-1dp', '2dp', '-2dp'

class MainWindow(FloatLayout):
    pass

class SideBar(FloatLayout):
    pass

class ScreenManagement(ScreenManager):
    pass

class HomeScreen(Screen, FloatLayout):
    pass

class DeviceScreen(Screen):
    pass

class PhaseTimeFrequencyTabs(TabbedPanel):
    pass

class ChannelStimulationTabs(TabbedPanel):
    pass

class BurstContinousStimulationTabs(TabbedPanel):
    pass

class BurstUniformStimulationTabs(TabbedPanel):
    pass

class TerminationTabs(TabbedPanel):
    pass

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class MessagePopup(Popup):
    pass

class ValueError(Popup):
    pass

class BurstLostError(Popup):
    pass

class periodLostError(Popup):
    pass

class ChargeImbalanceError(Popup):
    pass

class PeriodBiggerError(Popup):
    pass
