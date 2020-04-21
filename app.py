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
from kivy.uix.dropdown import DropDown
import httplib2
import json
from urllib.request import urlopen
import urllib.request
import serial
import numpy
import matplotlib.pyplot as plt
from drawnow import *
import asyncio
from bleak import discover,BleakClient

MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
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


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
								 RecycleBoxLayout):
	''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
	''' Add selection support to the Label '''
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		''' Catch and handle the view changes '''
		self.index = index
		return super(SelectableLabel, self).refresh_view_attrs(
			rv, index, data)

	def on_touch_down(self, touch):
		''' Add selection on touch down '''
		if super(SelectableLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		''' Respond to the selection of items in the view. '''
		self.selected = is_selected
		if is_selected:
			print("selection changed to {0}".format(rv.data[index]))
			loop = asyncio.get_event_loop()
			loop.run_until_complete(connect(rv.data[index]['text'].split(': ')[0],loop))
		else:
			print("selection removed for {0}".format(rv.data[index]))

class BLE_RV(RecycleView):
	def __init__(self, **kwargs):
		super(BLE_RV, self).__init__(**kwargs)
		self.data = []

class NS_Window(Widget):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.devices = ['Test']

	async def ble_discover(self):
		self.devices = await discover()
		self.ble_rv.data = [{'text':str(i)} for i in self.devices]



	def connect_to_bluetooth(self):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.ble_discover())



class App(App):
	def build(self):
		return NS_Window()

if __name__ == '__main__':
	App().run()
