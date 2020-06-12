from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.properties import ObjectProperty,NumericProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelStrip
from bleak import discover, BleakClient, BleakScanner
from bleak.exc import BleakDotNetTaskError, BleakError
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput

import asyncio
import threading
from scipy import signal
import numpy as np
import pprint
from kivy.config import Config
Config.set('graphics', 'width', 1024)
Config.set('graphics', 'height', 768)
Config.set('graphics', 'resizable', 'False')
"""Must be below config setting, otherwise it's reset"""
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
import matplotlib.pyplot as plt

devices_dict = {}
ids = [
    'screen_manager',
    'side_bar',
    'device_rv',
    'home_button',
    'new_device_button',
    'side_bar_title',
    'home_screen',
    'device_screen',
    'home_screen_windows',
    'device_screen_device_tabs',
    'device_settings',
    'device_advanced_settings',
    'stimulation_log_tab',
    'channel_1_stop_button',
    'channel_1_save_button',
    'channel_1_start_button',
    'channel_1_output_current_input',
    'channel_1_termination_tabs',
    'channel_1_cathodic_anodic_toggle',
    'channel_1_ramp_up_toggle',
    'channel_1_electrode_toggle',
    'channel_1_electrode_button',
    'channel_2_stop_button',
    'channel_2_save_button',
    'channel_2_start_button',
    'channel_2_output_current_input',
    'channel_2_termination_tabs',
    'channel_2_cathodic_anodic_toggle',
    'channel_2_ramp_up_toggle',
    'channel_2_electrode_toggle',
    'channel_2_electrode_button',
    'termination_tabs_time_input_1',
    'termination_tabs_duty_cycle_input_1',
    'termination_tabs_time_input_2',
    'termination_tabs_duty_cycle_input_2',
    'stimulation_log_tab_top_graph',
    'stimulation_log_tab_bottom_graph',
    'stimulation_log_tab_sample_info',
    'stimulation_log_tab_log_stop_button',
    'stimulation_log_tab_log_recording_button',
    'stimulation_log_save_log_button',
    'auto_shutdown_when_stim_is_finished',
    'auto_shutdown_when_surge_is_detected',
    'firmware_info_button',
    'hardware_info_button',
    'bootloader_access_button',
    'ramp_up_button',
    'ramp_up_input',
    'short_button',
    'continuity_check_button',
    'triggered_mode_button',
    'triggered_mode_toggle',
    'ramp_dac_button',
    'null_command_button',
    'debug_mode_button',
    'test_trigger_button',
    'all_off_button',
    'phase_2_button',
    'phase_1_button',
    'triggered_mode_toggle_none_button',
    'triggered_mode_toggle_phase_1_button',
    'triggered_mode_toggle_phase_2_button',
    'triggered_mode_toggle_phase_1_and_2_button',
    'triggered_mode_toggle_inter_stim_time_button',
    'ramp_up_text_input',
    'channel_1_stimulation_graph_display',
    'channel_2_stimulation_graph_display',
    'channel_2_cathodic_toggle',
    'channel_2_anodic_toggle',
    'channel_1_cathodic_toggle',
    'channel_1_anodic_toggle',
    'channel_1_inter_burst_delay_input',
    'channel_1_burst_duration_input',
    'channel_2_inter_burst_delay',
    'channel_2_burst_duration',
    'channel_1_inter_phase_delay_input',
    'channel_1_phase_time_input',
    'channel_2_inter_phase_delay_input',
    'channel_2_phase_time_input',
    'channel_1_burst_frequency'
]

class custom_test(TextInput):
    pass

def update_graph():
    graph = get_squarewave_plot()
    App.get_running_app().get_components('channel_1_stimulation_graph_display').clear_widgets()
    App.get_running_app().get_components('channel_1_stimulation_graph_display').add_widget(graph)

def get_squarewave_plot():
    settings = App.get_running_app().get_channel_1_graph_variables()
    print(settings['channel_1_burst_frequency'])

    burst = settings['channel_1_burst_uniform_stimulation_tab'] == 'Burst Stimulation'
    if burst:
        bursttime = settings['channel_1_burst_duration_input'] if settings['channel_1_burst_duration_input'] != "" else 0
        bursttime = int(bursttime) * 1000
        interburst = settings['channel_1_inter_burst_delay_input'] if settings['channel_1_inter_burst_delay_input'] != "" else 0
        interburst = int(interburst) * 1000 * 1000
        # TODO:======================================================
        # if interburst == 0:
        #     burstfrequency = input("burstfrequency (Hz): \n")
        #     burstfrequency = int(burstfrequency)
        #     interburst = 1000000 / burstfrequency - bursttime

    anodic = settings['channel_1_anodic_toggle'] == 'down'
    current = int(settings['channel_1_output_current_input']) if settings['channel_1_output_current_input'] != "" else 0
    phasetime1 = int(settings['channel_1_phase_1_time_input']) if settings['channel_1_phase_1_time_input'] != "" else 0
    phasetime2 = int(settings['channel_1_phase_2_time_input']) if settings['channel_1_phase_2_time_input'] != "" else 0
    interphase = int(settings['channel_1_inter_phase_delay_input']) if settings['channel_1_inter_phase_delay_input'] != "" else 0
    interstim = 0
    if settings['channel_1_phase_time_frequency_tab'] == 'Phase Time':
        interstim = int(settings['channel_1_inter_stim_delay_input']) if settings['channel_1_inter_stim_delay_input'] != "" else 0
    if settings['channel_1_phase_time_frequency_tab'] == 'Frequency':
        wavefrequency = int(settings['channel_1_frequency_input']) if settings['channel_1_frequency_input'] != "" else 0
        interstim = 1000000 / wavefrequency - phasetime1 - phasetime2 - interphase

    if anodic:
        andoic_y_axis = [0, 1, 1, 0, 0, -1, -1, 0, 0]
        V = [i * current * 0.001 for i in andoic_y_axis]
    else:
        cathodic_y_axis = [0, -1, -1, 0, 0, 1, 1, 0, 0]
        V = [i * current * 0.001 for i in cathodic_y_axis]

    T = [
        0,
        0,
        phasetime1,
        phasetime1,
        phasetime1+interphase,
        phasetime1+interphase,
        phasetime1+phasetime2+interphase,
        phasetime1+phasetime2+interphase,
        phasetime1+phasetime2+interphase+interstim
    ]
    # if its uniform stim, graph stop plotting after one peroid
    # if its burst stim, graph stop plotting after one burst peroid
    if burst and bursttime != 0 and interburst != 0:
        # constantly add last element of previous "T list"to all element in previous T to make a new list of timing for next peroid. and then join all lists together to form a set for y-axis data
        b = T.copy()
        while (b[len(b) - 1] < (bursttime + interburst)):
            for i in range(len(b)):
                b[i] = T[i] + b[len(b) - 1]
            print("here")
            T = T + b

        # change the T[-1]to bursttime
        T[len(T) - 1] = bursttime
        # count how many element in the T list, divide by the 9, and repeat V list this many time, make set V2
        # V * (len(T) / 9)
        m = V.copy()
        for i in range(int(len(T) / 9.0 - 1)):
            m = m + V
        V = m
        # add one more element to T, that is bursttime + interburst
        T.append(bursttime + interburst)
        V.append(0)
    # if settings['channel_1_burst_uniform_stimulation_tab'] == 'Uniform Stimulation':

    plt.close("all")
    plt.plot(T, V)
    plt.xlabel('time (us)')
    plt.ylabel('voltage (mV)')

    return FigureCanvasKivyAgg(plt.gcf())

def update_graph_on_text_channel_1(instance, value):
    update_graph()


def update_graph_on_toggle_channel_1(button,state):
    update_graph()

live_update_references = {
    'channel_1_stimulation_graph_display': [
        'termination_tabs_time_input_1',
        'termination_tabs_duty_cycle_input_1',
        'channel_1_output_current_input',
        'channel_1_cathodic_toggle',
        'channel_1_inter_stim_delay_input',
        'channel_1_anodic_toggle',
        'channel_1_ramp_up_toggle',
        'channel_1_electrode_toggle',
        'channel_1_inter_burst_delay_input',
        'channel_1_burst_duration_input',
        'channel_1_inter_phase_delay_input',
        'channel_1_phase_1_time_input',
        'channel_1_phase_2_time_input',
        'channel_1_frequency_input',
        'channel_1_burst_frequency'
    ]
}

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


class BurstUniformStimulationTabs(TabbedPanel):
    pass


class TerminationTabs(TabbedPanel):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class AddDevicePopup(Popup):
    async def ble_discover(self):
        self.devices = await discover(0.5)
        self.ble_rv.data = [{'text': str(i.address)} for i in self.devices if i.address is not None]

    def BluetoothDiscoverLoop(self):
        data = App.get_running_app().device_data
        if len(data) == 0:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.ble_discover())
        else:
            self.ble_rv.data = data

    def Close(self):
        data = App.get_running_app().root.side_bar.device_rv.data

        for j in devices_dict.keys():
            adding = True
            for i in data:
                if i['text'] == j:
                    adding = False
            if adding and devices_dict[j]:
                App.get_running_app().root.side_bar.device_rv.data.append({'text': j})
        # print(App.get_running_app().root.side_bar.device_rv.data)
        self.dismiss()


class DT_TPS(TabbedPanelStrip):
    pass


class DeviceTabs(TabbedPanel, DT_TPS):
    def __init__(self, **kargs):
        super(DeviceTabs, self).__init__(**kargs)
        self._tab_layout.padding = '2dp', '-1dp', '2dp', '-2dp'


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


class DeviceRV(RecycleView):
    def __init__(self, **kwargs):
        super(DeviceRV, self).__init__(**kwargs)
        self.selected_count = 0
        self.buffer_count = 0
        self.deselected_clock = {}


class ConnectedDeviceSelectableLabel(RecycleDataViewBehavior, FloatLayout):
    index = None  # this is the index of the label in the recyclerview
    selected = BooleanProperty(False)  # true if selected, false otherwise
    selectable = BooleanProperty(True)  # permissions as to whether it is selectable
    deselected = False

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self._label.text = data['text']
        return super(ConnectedDeviceSelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(ConnectedDeviceSelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        # print(index, is_selected, self.selected, self.deselected)
        if not is_selected and self.selected:
            # print("here")
            self.selected = False
            App.get_running_app().root.screen_manager.transition.direction = 'down'
            App.get_running_app().root.screen_manager.current = 'home'
            App.get_running_app().root.side_bar.device_rv.selected_count -= 1
            self.deselected = True
            App.get_running_app().root.side_bar.device_rv.deselected_clock[rv.data[index]['text']] = 0
            return None
        elif is_selected and not self.selected and (not self.deselected or App.get_running_app().root.side_bar.device_rv.deselected_clock[rv.data[index]['text']] > 0):
            self.selected = True
            App.get_running_app().root.screen_manager.transition.direction = 'up'
            App.get_running_app().root.screen_manager.current = 'device'
            App.get_running_app().root.side_bar.device_rv.selected_count += 1


            for i in live_update_references['channel_1_stimulation_graph_display']:
                if 'input' in i:
                    App.get_running_app().get_components(i).bind(text=update_graph_on_text_channel_1)
                if 'toggle' in i:
                    App.get_running_app().get_components(i).bind(state=update_graph_on_toggle_channel_1)
                print(i,App.get_running_app().get_components(i))

        elif is_selected and self.selected:
            App.get_running_app().root.side_bar.device_rv.selected_count -= 1
            self.selected = False
            if App.get_running_app().root.side_bar.device_rv.selected_count == 0:
                App.get_running_app().root.screen_manager.transition.direction = 'down'
                App.get_running_app().root.screen_manager.current = 'home'
        self.deselected = False
        keys = App.get_running_app().root.side_bar.device_rv.deselected_clock.keys()
        for k in keys:
            App.get_running_app().root.side_bar.device_rv.deselected_clock[k] += 1

        # for i in ids:
        #     print(App.get_running_app().get_components(i))

async def ble_discover(loop, time):
    task1 = loop.create_task(discover(time))
    await asyncio.wait([task1])
    return task1

def BluetoothDiscoverLoop():
    time = 0.5
    while App.get_running_app().search:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(1)
        r1 = loop.run_until_complete(ble_discover(loop, time))
        devices = r1.result()
        data = [{'text': str(i.address)} for i in devices if i.address is not None]
        App.get_running_app().device_data = data
        if time < 10:
            time += 1

class NeuroStimApp(App):
    def __init__(self, kvloader):
        super(NeuroStimApp, self).__init__()
        self.kvloader = kvloader
        self.device_data = []
        self.search = True
        self.t = threading.Thread(target=BluetoothDiscoverLoop)
        self.t.daemon = True
        self.t.start()

    def get_channel_1_graph_variables(self):
        return {
            'channel_1_termination_tabs': self.get_components('channel_1_termination_tabs').current_tab.text,
            'channel_1_phase_time_frequency_tab': self.get_components('channel_1_phase_time_frequency_tab').current_tab.text,
            'channel_1_burst_uniform_stimulation_tab': self.get_components('channel_1_burst_uniform_stimulation_tab').current_tab.text,
            'channel_1_inter_burst_delay_input': self.get_components('channel_1_inter_burst_delay_input').text,
            'channel_1_burst_duration_input': self.get_components('channel_1_burst_duration_input').text,
            'channel_1_inter_phase_delay_input': self.get_components('channel_1_inter_phase_delay_input').text,
            'channel_1_inter_stim_delay_input': self.get_components('channel_1_inter_stim_delay_input').text,
            'channel_1_phase_1_time_input': self.get_components('channel_1_phase_1_time_input').text,
            'channel_1_phase_2_time_input': self.get_components('channel_1_phase_2_time_input').text,
            'channel_1_frequency_input': self.get_components('channel_1_frequency_input').text,
            'termination_tabs_time_input_1': self.get_components('termination_tabs_time_input_1').text,
            'termination_tabs_duty_cycle_input_1': self.get_components('termination_tabs_duty_cycle_input_1').text,
            'channel_1_output_current_input': self.get_components('channel_1_output_current_input').text,
            'channel_1_cathodic_toggle':self.get_components('channel_1_cathodic_toggle').state,
            'channel_1_anodic_toggle':self.get_components('channel_1_anodic_toggle').state,
            'channel_1_ramp_up_toggle':self.get_components('channel_1_ramp_up_toggle').state,
            'channel_1_electrode_toggle':self.get_components('channel_1_electrode_toggle').state,
            'channel_1_burst_frequency':self.get_components('channel_1_burst_frequency').text
        }

    def get_components(self, id):
        if id == 'screen_manager':
            return self.root.screen_manager
        if id == 'side_bar':
            return self.root.side_bar
        if id == 'device_rv':
            return self.root.side_bar.device_rv
        if id == 'home_button':
            return self.root.side_bar.home_button
        if id == 'new_device_button':
            return self.root.side_bar.new_device_button
        if id == 'side_bar_title':
            return self.root.side_bar.side_bar_title
        if id == 'home_screen':
            return self.root.screen_manager.home_screen
        if id == 'device_screen':
            return self.root.screen_manager.device_screen
        if id == 'home_screen_windows':
            return self.root.screen_manager.home_screen.windows
        if id == 'device_screen_device_tabs':
            return self.root.screen_manager.device_screen.device_tabs
        if id == 'device_settings':
            return self.root.screen_manager.device_screen.device_tabs.device_settings
        if id == 'device_advanced_settings':
            return self.root.screen_manager.device_screen.device_tabs.advanced_settings
        if id == 'stimulation_log_tab':
            return self.root.screen_manager.device_screen.device_tabs.stimulation_log_tab
        if id == 'stimulation_tabs':
            return self.get_components('device_settings').stimulation_tabs

        if id == 'channel_1_stop_button':
            return self.get_components('stimulation_tabs').channel_1_stop_button
        if id == 'channel_1_save_button':
            return self.get_components('stimulation_tabs').channel_1_save_button
        if id == 'channel_1_start_button':
            return self.get_components('stimulation_tabs').channel_1_start_button
        if id == 'channel_1_output_current_input':
            return self.get_components('stimulation_tabs').channel_1_output_current_input
        if id == 'channel_1_termination_tabs':
            return self.get_components('stimulation_tabs').channel_1_termination_tabs
        if id == 'channel_1_cathodic_anodic_toggle':
            return self.get_components('stimulation_tabs').channel_1_cathodic_anodic_toggle
        if id == 'channel_1_cathodic_toggle':
            return self.get_components('channel_1_cathodic_anodic_toggle').cathodic
        if id == 'channel_1_anodic_toggle':
            return self.get_components('channel_1_cathodic_anodic_toggle').anodic
        if id == 'channel_1_ramp_up_toggle':
            return self.get_components('stimulation_tabs').channel_1_ramp_up_toggle
        if id == 'channel_1_electrode_toggle':
            return self.get_components('stimulation_tabs').channel_1_electrode_toggle
        if id == 'channel_1_electrode_button':
            return self.get_components('stimulation_tabs').channel_1_electrode_button
        if id =='channel_1_burst_frequency':
            return self.get_components('channel_1_burst_uniform_stimulation_tab').burst_frequency

        if id == 'channel_2_stop_button':
            return self.get_components('stimulation_tabs').channel_2_stop_button
        if id == 'channel_2_save_button':
            return self.get_components('stimulation_tabs').channel_2_save_button
        if id == 'channel_2_start_button':
            return self.get_components('stimulation_tabs').channel_2_start_button
        if id == 'channel_2_output_current_input':
            return self.get_components('stimulation_tabs').channel_2_output_current_input
        if id == 'channel_2_termination_tabs':
            return self.get_components('stimulation_tabs').channel_2_termination_tabs
        if id == 'channel_2_cathodic_anodic_toggle':
            return self.get_components('stimulation_tabs').channel_2_cathodic_anodic_toggle
        if id == 'channel_2_cathodic_toggle':
            return self.get_components('channel_2_cathodic_anodic_toggle').cathodic
        if id == 'channel_2_anodic_toggle':
            return self.get_components('channel_2_cathodic_anodic_toggle').anodic
        if id == 'channel_2_ramp_up_toggle':
            return self.get_components('stimulation_tabs').channel_2_ramp_up_toggle
        if id == 'channel_2_electrode_toggle':
            return self.get_components('stimulation_tabs').channel_2_electrode_toggle
        if id == 'channel_2_electrode_button':
            return self.get_components('stimulation_tabs').channel_2_electrode_button

        if id == 'termination_tabs_time_input_1':
            return self.get_components('channel_1_termination_tabs').termination_tabs_time_input
        if id == 'termination_tabs_duty_cycle_input_1':
            return self.get_components('channel_1_termination_tabs').termination_tabs_duty_cycle_input

        if id == 'termination_tabs_time_input_2':
            return self.get_components('channel_2_termination_tabs').termination_tabs_time_input
        if id == 'termination_tabs_duty_cycle_input_2':
            return self.get_components('channel_2_termination_tabs').termination_tabs_duty_cycle_input

        if id == 'stimulation_log_tab_top_graph':
            return self.get_components('stimulation_log_tab').top_graph
        if id == 'stimulation_log_tab_bottom_graph':
            return self.get_components('stimulation_log_tab').bottom_graph
        if id == 'stimulation_log_tab_sample_info':
            return self.get_components('stimulation_log_tab').sample_info
        if id == 'stimulation_log_tab_log_stop_button':
            return self.get_components('stimulation_log_tab').log_stop_button
        if id == 'stimulation_log_tab_log_recording_button':
            return self.get_components('stimulation_log_tab').log_recording_button
        if id == 'stimulation_log_save_log_button':
            return self.get_components('stimulation_log_tab').save_log_button

        if id == 'auto_shutdown_when_stim_is_finished':
            return self.get_components('device_advanced_settings').auto_shutdown_when_stim_is_finished
        if id == 'auto_shutdown_when_surge_is_detected':
            return self.get_components('device_advanced_settings').auto_shutdown_when_surge_is_detected
        if id == 'firmware_info_button':
            return self.get_components('device_advanced_settings').firmware_info_button
        if id == 'hardware_info_button':
            return self.get_components('device_advanced_settings').hardware_info_button
        if id == 'bootloader_access_button':
            return self.get_components('device_advanced_settings').bootloader_access_button
        if id == 'ramp_up_button':
            return self.get_components('device_advanced_settings').ramp_up_button
        if id == 'ramp_up_input':
            return self.get_components('device_advanced_settings').ramp_up_input
        if id == 'short_button':
            return self.get_components('device_advanced_settings').short_button
        if id == 'continuity_check_button':
            return self.get_components('device_advanced_settings').continuity_check_button
        if id == 'triggered_mode_button':
            return self.get_components('device_advanced_settings').triggered_mode_button
        if id == 'triggered_mode_toggle':
            return self.get_components('device_advanced_settings').triggered_mode_toggle
        if id == 'ramp_dac_button':
            return self.get_components('device_advanced_settings').ramp_dac_button
        if id == 'null_command_button':
            return self.get_components('device_advanced_settings').null_command_button
        if id == 'debug_mode_button':
            return self.get_components('device_advanced_settings').debug_mode_button
        if id == 'test_trigger_button':
            return self.get_components('device_advanced_settings').test_trigger_button
        if id == 'all_off_button':
            return self.get_components('device_advanced_settings').all_off_button
        if id == 'phase_2_button':
            return self.get_components('device_advanced_settings').phase_2_button
        if id == 'phase_1_button':
            return self.get_components('device_advanced_settings').phase_1_button

        if id == 'ramp_up_text_input':
            return self.get_components('ramp_up_input').ramp_up_text_input

        if id == 'triggered_mode_toggle_none_button':
            return self.get_components('triggered_mode_toggle').none_button
        if id == 'triggered_mode_toggle_phase_1_button':
            return self.get_components('triggered_mode_toggle').phase_1_button
        if id == 'triggered_mode_toggle_phase_2_button':
            return self.get_components('triggered_mode_toggle').phase_2_button
        if id == 'triggered_mode_toggle_phase_1_and_2_button':
            return self.get_components('triggered_mode_toggle').phase_1_and_2_button
        if id == 'triggered_mode_toggle_inter_stim_time_button':
            return self.get_components('triggered_mode_toggle').inter_stim_time_button

        if id == 'channel_1_phase_time_frequency_tab':
            return self.get_components('stimulation_tabs').channel_1_phase_time_frequency_tab
        if id == 'channel_1_burst_uniform_stimulation_tab':
            return self.get_components('stimulation_tabs').channel_1_burst_uniform_stimulation_tab
        if id == 'channel_2_phase_time_frequency_tab':
            return self.get_components('stimulation_tabs').channel_2_phase_time_frequency_tab
        if id == 'channel_2_burst_uniform_stimulation_tab':
            return self.get_components('stimulation_tabs').channel_2_burst_uniform_stimulation_tab

        if id == 'channel_1_inter_burst_delay_input':
            return self.get_components('channel_1_burst_uniform_stimulation_tab').inter_burst_delay
        if id == 'channel_1_burst_duration_input':
            return self.get_components('channel_1_burst_uniform_stimulation_tab').burst_duration
        if id == 'channel_2_inter_burst_delay':
            return self.get_components('channel_2_burst_uniform_stimulation_tab').inter_burst_delay
        if id == 'channel_2_burst_duration':
            return self.get_components('channel_2_burst_uniform_stimulation_tab').burst_duration

        if id == 'channel_1_inter_phase_delay_input':
            return self.get_components('channel_1_phase_time_frequency_tab').channel_1_inter_phase_delay_input
        if id == 'channel_1_inter_stim_delay_input':
            return self.get_components('channel_1_phase_time_frequency_tab').channel_1_inter_stim_delay_input
        if id == 'channel_1_phase_1_time_input':
            return self.get_components('channel_1_phase_time_frequency_tab').channel_1_phase_1_time_input
        if id == 'channel_1_phase_2_time_input':
            return self.get_components('channel_1_phase_time_frequency_tab').channel_1_phase_2_time_input
        if id == 'channel_1_frequency_input':
            return self.get_components('channel_1_phase_time_frequency_tab').channel_1_frequency_input
        if id == 'channel_2_inter_phase_delay_input':
            return self.get_components('channel_2_phase_time_frequency_tab').inter_phase_delay
        if id == 'channel_2_phase_time_input':
            return self.get_components('channel_2_phase_time_frequency_tab').phase_time

        if id == 'channel_1_stimulation_graph_display':
            return self.get_components('stimulation_tabs').channel_1_stimulation_graph_display
        if id == 'channel_2_stimulation_graph_display':
            return self.get_components('stimulation_tabs').channel_2_stimulation_graph_display
        print("missing id: ",id)
        return None

    def build(self):
        return MainWindow()

    def on_stop(self):
        '''Event handler for the `on_stop` event which is fired when the
        application has finished running (i.e. the window is about to be
        closed).
        '''
        self.search = False

if __name__ == '__main__':
    kvloader = Builder.load_file("ui2.kv")
    App = NeuroStimApp(kvloader)
    App.run()
