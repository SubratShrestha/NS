import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel


class HomeScreen(Screen):
    pass

class DeviceScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class DeviceTabs(TabbedPanel):
    pass

class DeviceSettings(BoxLayout):
    pass

class PhaseTimeFrequencyTabs(TabbedPanel):
    pass

class BurstUniformStimulationTabs(TabbedPanel):
    pass

class TerminationTabs(TabbedPanel):
    pass

class CathodicAnodicToggle(BoxLayout):
    pass

kv_loader = Builder.load_file("neurostim.kv")


class HomeLayout(FloatLayout):
    def __init__(self):
        super(HomeLayout, self).__init__()

class NeuroStimApp(App):
    def build(self):
        return kv_loader

if __name__ == "__main__":
    NeuroStimApp().run()
