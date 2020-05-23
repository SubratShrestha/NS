from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen


class MainWindow(GridLayout):
	pass


class SideBar(FloatLayout):
	pass


class ScreenManagement(ScreenManager):
	pass


class HomeScreen(Screen, FloatLayout):
	pass


class DeviceScreen(Screen):
	pass


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
