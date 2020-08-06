uuid_format = False # True
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelStrip, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
import re
import asyncio
import threading
from scipy import signal
import numpy as np
import pprint
import math
from kivy.config import Config
Config.set('graphics', 'width', 1024)
Config.set('graphics', 'height', 768)
Config.set('graphics', 'resizable', 'False')

"""Must be below config setting, otherwise it's reset"""
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
import matplotlib.pyplot as plt
from kivy_matplotlib import MatplotFigure, MatplotNavToolbar

RAMP_UP_WRITE_CHAR = '02000000-0000-0000-0000-00000000010d'
SHORT_ELECTRODE_WRITE_CHAR = '02000000-0000-0000-0000-00000000010e'
RAMP_UP_READ_CHAR = '02000000-0000-0000-0000-00000000000d'
SHORT_ELECTRODE_READ_CHAR = '02000000-0000-0000-0000-00000000000e'

BATTERY_LEVEL_CHAR = '00002a19-0000-1000-8000-00805f9b34fb'
CHANNEL_NUM_CHAR = '01000000-0000-0000-0000-000000000006'
MAX_FREQ_CHAR = '01000000-0000-0000-0000-000000000007'
OTA_SUPPORT_CHAR = '01000000-0000-0000-0000-000000000008'

PHASE_ONE_WRITE_CHAR = '02000000-0000-0000-0000-000000000103'
PHASE_TWO_WRITE_CHAR = '02000000-0000-0000-0000-000000000105'
STIM_AMP_WRITE_CHAR = '02000000-0000-0000-0000-000000000102'
INTER_PHASE_GAP_WRITE_CHAR = '02000000-0000-0000-0000-000000000104'
INTER_STIM_DELAY_WRITE_CHAR = '02000000-0000-0000-0000-000000000106'
PULSE_NUM_WRITE_CHAR = '02000000-0000-0000-0000-000000000107'
ANODIC_CATHOLIC_FIRST_WRITE_CHAR = '02000000-0000-0000-0000-000000000108'
STIM_TYPE_WRITE_CHAR = '02000000-0000-0000-0000-000000000109'
BURST_NUM_WRITE_CHAR = '02000000-0000-0000-0000-00000000010a'
INTER_BURST_DELAY_WRITE_CHAR = '02000000-0000-0000-0000-00000000010b'
SERIAL_COMMAND_INPUT_CHAR = '02000000-0000-0000-0000-000000000101'
# PULSE_NUM_IN_ONE_BRUST_WRITE_CHAR = # Mitchell

INTER_PHASE_GAP_READ_CHAR = '02000000-0000-0000-0000-000000000004'
PHASE_ONE_READ_CHAR = '02000000-0000-0000-0000-000000000003'
PHASE_TWO_READ_CHAR = '02000000-0000-0000-0000-000000000005'
STIM_AMP_READ_CHAR = '02000000-0000-0000-0000-000000000002'
INTER_STIM_DELAY_READ_CHAR = '02000000-0000-0000-0000-000000000006'
PULSE_NUM_READ_CHAR = '02000000-0000-0000-0000-000000000007'
ANODIC_CATHODIC_FIRST_READ_CHAR = '02000000-0000-0000-0000-000000000008'
STIM_TYPE_READ_CHAR = '02000000-0000-0000-0000-000000000009'
BURST_NUM_READ_CHAR = '02000000-0000-0000-0000-00000000000a'
INTER_BURST_DELAY_READ_CHAR = '02000000-0000-0000-0000-00000000000b'

"""======================================================================
Don't change this to match App.py
These are strictly for Windows.py
========================================================================="""
from multiprocessing.connection import Listener, Client
import threading

devices_dict = {}
ids = [
    'screen_manager',
    'side_bar',
    'device_rv',
    'home_button',
    'new_device_button',
    'home_screen',
    'device_screen',
    'home_screen_windows',
    'device_screen_device_tabs',
    'device_settings',
    'device_advanced_settings',
    'electrode_recording_tab',
    'stimulation_graph_display',
    'stop_button',
    'save_button',
    'start_button',
    'termination_tabs',
    'cathodic_anodic_toggle',
    'stimulation_graph_display',
    'stimulation_duration',
    'number_of_burst',
    'output_current_input',
    'cathodic_toggle',
    'anodic_toggle',
    'duty_cycle_input',
    'burst_period_input',
    'inter_stim_delay_input',
    'inter_phase_delay_input',
    'phase_1_time_input',
    'phase_2_time_input',
    'channel_1_frequency_input',
    'electrode_recording_tab_top_graph',
    'electrode_recording_tab_bottom_graph',
    'electrode_recording_tab_sample_info',
    'electrode_recording_tab_log_stop_button',
    'electrode_recording_tab_log_recording_button',
    'electrode_recording_save_log_button',
    'auto_shutdown_when_stim_is_finished',
    'auto_shutdown_when_surge_is_detected',
    'firmware_info_button',
    'hardware_info_button',
    'bootloader_access_button',
    'ramp_up_button',
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
]

class custom_test(TextInput):
    pass

def update_graph():
    graph = get_squarewave_plot()
    App.get_running_app().get_components('stimulation_graph_display').clear_widgets()
    App.get_running_app().get_components('stimulation_graph_display').add_widget(graph)

def get_stimulator_input():
    burstmode = False
    burstperiod = False
    burstduration = False
    dutycycle = False
    interburst = False
    anodic = False
    current = False
    phasetime1 = False
    phasetime2 = False
    interstim = False
    frequency = False
    burstfrequency = False
    pulsenumber = False
    stimduration = False
    burstnumber = False
    pulseperoid = False

    settings = App.get_running_app().get_graph_variables()

    burstmode = settings['burst_continous_stimulation_tab'] == 'Burst Stimulation'
    if burstmode:
        burstperiod = settings['burst_period_input'] if settings['burst_period_input'] != "" else 0
        burstperiod = int(burstperiod) * 1000
        dutycycle = settings['duty_cycle_input'] if settings['duty_cycle_input'] != "" else 0
        dutycycle = int(dutycycle) / 100
        burstduration = dutycycle * burstperiod
        interburst = burstperiod - burstduration


    anodic = settings['anodic_toggle'] == 'down'
    current = int(settings['output_current_input']) if settings['output_current_input'] != "" else 0
    phasetime1 = int(settings['phase_1_time_input']) if settings['phase_1_time_input'] != "" else 0
    phasetime2 = int(settings['phase_2_time_input']) if settings['phase_2_time_input'] != "" else 0
    interphase = int(settings['inter_phase_delay_input']) if settings['inter_phase_delay_input'] != "" else 0
    interstim = 0
    if settings['phase_time_frequency_tab'] == 'Phase Time':
        interstim = int(settings['inter_stim_delay_input']) if settings['inter_stim_delay_input'] != "" else 0
    if settings['phase_time_frequency_tab'] == 'Frequency':
        frequency = int(settings['frequency_input']) if settings['frequency_input'] != "" else 0
        if frequency != 0:
            interstim = 1000000 / frequency - phasetime1 - phasetime2 - interphase
    pulseperoid = phasetime1 + phasetime2 + interphase + interstim


    if  settings['termination_tabs'] == 'Stimulate forever':
        stimduration = int(float("inf"))
    if  settings['termination_tabs'] == 'Stimulation duration':
        stimduration = int(settings['stimulation_duration']) if settings['stimulation_duration'] != "" else 0
    if  settings['termination_tabs'] == 'Number of burst':
        burstduration = int(settings['number_of_burst']) if settings['number_of_burst'] != "" else 0

    if burstmode:
        if burstduration and stimduration:
            burstnumber = stimduration // burstduration
        if burstduration and burstperiod:
            pulsenumber = burstduration // burstperiod
        if burstduration != 0:
            burstfrequency = 10000000 / burstduration
    else:
        if stimduration:
            pulsenumber = stimduration // pulseperoid
    return settings, int(burstmode), int(burstperiod), int(burstduration), int(dutycycle), int(interburst), int(anodic), int(current), int(interphase), int(phasetime1), int(phasetime2), int(interstim), int(frequency), 0 if settings['ramp_up_button'] == 'normal' else 1, 0 if settings['short_button'] == 'normal' else 1, int(burstfrequency), int(pulsenumber), int(stimduration), int(burstnumber), int(pulseperoid)

def get_squarewave_plot():
    settings, burstmode, burstperiod, burstduration, dutycycle, interburst, anodic, current, interphase, phasetime1, phasetime2, interstim, frequency, ramp_up, short, burstfrequency, pulsenumber, stimduration, burstnumber, pulseperoid = get_stimulator_input()

    # points on y-axis
    andoic = [0, 1, 1, 0, 0, -1, -1, 0, 0]
    cathodic = [0, -1, -1, 0, 0, 1, 1, 0, 0]
    if anodic:
        I = [i * current for i in andoic]
    else:
        I = [i * current for i in cathodic]

    # points on x-axis
    # timing of first cycle
    T = [0, 0, phasetime1, phasetime1, phasetime1 + interphase, phasetime1 + interphase,
         phasetime1 + phasetime2 + interphase, phasetime1 + phasetime2 + interphase,
         phasetime1 + phasetime2 + interphase + interstim]

    # if its continuous stim, graph stop plotting after one period
    # if its burst stim, graph stop plotting after one burst period
    if burstmode:
        # constantly add last element of previous "T list"to all element in previous T to make the point on y-axis
        b = T.copy()
        while (b[len(b) - 1] + pulseperoid < (burstduration)):
            for i in range(len(b)):
                b[i] = T[i] + b[len(b) - 1]
            T = T + b

        # change the T[-1]to burstduration
        T[len(T) - 1] = burstduration
        # count how many element in the T list, divide by the 9, and repeat V list this many time, make set V2
        m = I.copy()
        for i in range(int(len(T) / 9.0 - 1)):
            m = m + I
        I = m
        # add one more element to T, that is burstduration + interburst
        T.append(burstduration + interburst)
        I.append(0)

    if burstduration > pulseperoid:
        plt.close("all")
        plt.plot(T, I)
        plt.xlabel('Time (us)')
        plt.ylabel('Current (uA)')

    return FigureCanvasKivyAgg(plt.gcf())

def send_to_neurostimulator_via_ble(button, state):
    if state == 'down':
        print("send_to_neurostimulator_via_ble")
        settings, burstmode, burstperiod, burstduration, dutycycle, interburst, anodic, current, interphase, phasetime1, phasetime2, interstim, frequency, ramp_up, short, burstfrequency, pulsenumber, stimduration, burstnumber, pulseperoid = get_stimulator_input()

        if stimduration is not None and math.isinf(stimduration):
            if burstmode:
                burstnumber = 0
            else:
                pulsenumber = 0

        if uuid_format:
            data = {
                'mac_addr': App.get_running_app().connected_device_mac_addr,
                PHASE_ONE_WRITE_CHAR: phasetime1,
                PHASE_TWO_WRITE_CHAR:phasetime2,
                ANODIC_CATHOLIC_FIRST_WRITE_CHAR:anodic,
                STIM_AMP_WRITE_CHAR:current,
                STIM_TYPE_WRITE_CHAR:burstmode,
                INTER_PHASE_GAP_WRITE_CHAR:interphase,
                INTER_BURST_DELAY_WRITE_CHAR:interburst,
                # BURST_NUM_WRITE_CHAR: int(burstmode/burstperiod) if burstperiod != 0 else 0,
                BURST_NUM_WRITE_CHAR:burstnumber,
                INTER_STIM_DELAY_WRITE_CHAR:interstim,
                # PULSE_NUM_WRITE_CHAR: int(burstduration/burstperiod) if burstperiod != 0 else 0,
                PULSE_NUM_WRITE_CHAR:pulsenumber,
                # PULSE_NUM_IN_ONE_BRUST_WRITE_CHAR:pulsenumber, # Mitchell
                RAMP_UP_WRITE_CHAR:ramp_up,
                SHORT_ELECTRODE_WRITE_CHAR:short
            }
            print("send_to_neurostimulator_via_ble->send_via_ble", data)
            App.get_running_app().send_via_ble(data)
        else:
            data = {
                'mac_addr': App.get_running_app().connected_device_mac_addr,
                SERIAL_COMMAND_INPUT_CHAR: [
                    'stim_amp:{}'.format(current),
                    'stim_type:{}'.format(burstmode),
                    'anodic_cathodic:{}'.format(anodic),
                    'phase_one_time:{}'.format(phasetime1),
                    'inter_phase_gap:{}'.format(interphase),
                    'phase_two_time:{}'.format(phasetime2),
                    'inter_stim_delay:{}'.format(interstim),
                    'pulse_num:{}'.format(pulsenumber),
                    'pulse_num_in_one_burst:{}'.format(pulsenumber),
                    'burst_num:{}'.format(burstnumber),
                    'inter_burst_delay:{}'.format(interburst),
                    'ramp_up:{}'.format(ramp_up),
                    'short_electrode:{}'.format(short)
                ]
            }
            print("send_to_neurostimulator_via_ble->send_via_ble", data)
            App.get_running_app().send_via_ble(data)

def update_graph_on_text_channel_1(instance, value):
    update_graph()

def update_graph_on_toggle_channel_1(button,state):
    update_graph()


live_update_references = {
    'stimulation_graph_display': [
        'stimulation_duration',
        'number_of_burst',
        'output_current_input',
        'cathodic_toggle',
        'inter_stim_delay_input',
        'anodic_toggle',
        'duty_cycle_input',
        'burst_period_input',
        'inter_phase_delay_input',
        'phase_1_time_input',
        'phase_2_time_input',
        'channel_1_frequency_input',
        'start_button'
    ]
}



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

class AddDevicePopup(Popup):

    def BluetoothDiscoverLoop(self):
        data = []
        for i in App.get_running_app().device_data:
            if i['text'] not in devices_dict:
                data.append(i)
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
                App.get_running_app().send_via_ble(j)
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
            devices_dict[rv.data[index]['text']] = True


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
        if not is_selected and self.selected:
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


            for i in live_update_references['stimulation_graph_display']:
                if 'input' in i:
                    App.get_running_app().get_components(i).bind(text=update_graph_on_text_channel_1)
                if 'toggle' in i:
                    App.get_running_app().get_components(i).bind(state=update_graph_on_toggle_channel_1)
                if 'start_button' == i:
                    App.get_running_app().get_components(i).bind(state=send_to_neurostimulator_via_ble)

                print(i,App.get_running_app().get_components(i))
                App.get_running_app().connected_device_mac_addr = self.text
            # set_graph_default_values(self.text)
            device_char_data = App.get_running_app().device_char_data
            print("device_char_data:\t", device_char_data)
            if self.text in device_char_data:
                print("updating device battery level")
                device_char_data = device_char_data[self.text]
                if 'BATTERY_LEVEL_CHAR' in device_char_data:
                    battery_level = int(device_char_data['BATTERY_LEVEL_CHAR'])
                    self.battery_percentage.text = str(battery_level)+'%'
                    if battery_level <= 33:
                        self.battery_icon.source = './icons/battery.png'
                    else:
                        self.battery_icon.source = './icons/full_battery.png'



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

class NeuroStimApp(App):
    def __init__(self, kvloader):
        super(NeuroStimApp, self).__init__()
        self.kvloader = kvloader
        self.device_data = []

        """======================================================================
        Don't change this to match App.py
        These are strictly for Windows.py
        ========================================================================="""
        self.thread = True
        self.discover_thread = threading.Thread(target=self.discover)
        self.discover_thread.start()

        self.send_address = None
        self.send_conn = None

        self.device_char_data = {}


    def send_via_ble(self, data):
        try:
            if self.send_conn is not None and not self.send_conn.closed:
                self.send_conn.send(data)
                print("send_via_ble->ble.py: ", data)
        except Exception as e:
            print(e)

    def discover(self):
        """======================================================================
        Don't change this to match App.py
        These are strictly for Windows.py
        ========================================================================="""
        address = ('localhost', 6000)
        listener = Listener(address, authkey=b'password')
        conn = listener.accept()
        round = 0
        while self.thread:
            msg = conn.recv()

            if isinstance(msg, list):
                self.device_data = msg
            elif isinstance(msg, dict):
                print(msg)
                mac_addr = msg.pop('mac_addr')
                data = msg
                self.device_char_data[mac_addr] = data

            if self.send_address is None:
                self.send_address = ('localhost', 6001)
                self.send_conn = Client(self.send_address, authkey=b'password')
            if round % 2 == 0:
                print("Updating reading from chars")
                for j in devices_dict.keys():
                    self.send_via_ble(j)
            round += 1
        listener.close()

    def get_graph_variables(self):
        def digit_clean(input):
            # Enforce the digit cleaning on the UI components as well
            input.text = re.sub("[^0-9]", "",input.text)
            return input.text
        return {
            'termination_tabs': self.get_components('termination_tabs').current_tab.text,
            'phase_time_frequency_tab': self.get_components('phase_time_frequency_tab').current_tab.text,
            'burst_continous_stimulation_tab': self.get_components('burst_continous_stimulation_tab').current_tab.text,
            'duty_cycle_input': digit_clean( self.get_components('duty_cycle_input')),
            'burst_period_input': digit_clean( self.get_components('burst_period_input')),
            'inter_phase_delay_input': digit_clean( self.get_components('inter_phase_delay_input')),
            'inter_stim_delay_input': digit_clean( self.get_components('inter_stim_delay_input')),
            'phase_1_time_input': digit_clean( self.get_components('phase_1_time_input')),
            'phase_2_time_input': digit_clean( self.get_components('phase_2_time_input')),
            'channel_1_frequency_input': digit_clean( self.get_components('channel_1_frequency_input')),
            'output_current_input': digit_clean( self.get_components('output_current_input')),
            'stimulation_duration': digit_clean( self.get_components('stimulation_duration')),
            'number_of_burst': digit_clean( self.get_components('number_of_burst')),
            'anodic_toggle': self.get_components('anodic_toggle').state,
            'ramp_up_button': self.get_components('ramp_up_button').state,
            'short_button': self.get_components('short_button').state
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
        if id == 'electrode_recording_tab':
            return self.root.screen_manager.device_screen.device_tabs.electrode_recording_tab
        if id == 'stimulation_tabs':
            return self.get_components('device_settings').stimulation_tabs

        if id == 'stop_button':
            return self.get_components('stimulation_tabs').stop_button
        if id == 'save_button':
            return self.get_components('stimulation_tabs').save_button
        if id == 'start_button':
            return self.get_components('stimulation_tabs').start_button
        if id == 'output_current_input':
            return self.get_components('stimulation_tabs').output_current_input
        if id == 'termination_tabs':
            return self.get_components('stimulation_tabs').termination_tabs
        if id == 'cathodic_anodic_toggle':
            return self.get_components('stimulation_tabs').cathodic_anodic_toggle
        if id == 'cathodic_toggle':
            return self.get_components('cathodic_anodic_toggle').cathodic
        if id == 'anodic_toggle':
            return self.get_components('cathodic_anodic_toggle').anodic

        if id == 'stimulation_duration':
            return self.get_components('termination_tabs').stimulation_duration
        if id == 'number_of_burst':
            return self.get_components('termination_tabs').number_of_burst

        if id == 'electrode_recording_tab_top_graph':
            return self.get_components('electrode_recording_tab').top_graph
        if id == 'electrode_recording_tab_bottom_graph':
            return self.get_components('electrode_recording_tab').bottom_graph
        if id == 'electrode_recording_tab_sample_info':
            return self.get_components('electrode_recording_tab').sample_info
        if id == 'electrode_recording_tab_log_stop_button':
            return self.get_components('electrode_recording_tab').log_stop_button
        if id == 'electrode_recording_tab_log_recording_button':
            return self.get_components('electrode_recording_tab').log_recording_button
        if id == 'electrode_recording_save_log_button':
            return self.get_components('electrode_recording_tab').save_log_button

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

        if id == 'phase_time_frequency_tab':
            return self.get_components('stimulation_tabs').phase_time_frequency_tab
        if id == 'burst_continous_stimulation_tab':
            return self.get_components('stimulation_tabs').burst_continous_stimulation_tab

        if id == 'duty_cycle_input':
            return self.get_components('burst_continous_stimulation_tab').duty_cycle
        if id == 'burst_period_input':
            return self.get_components('burst_continous_stimulation_tab').burst_period

        if id == 'inter_phase_delay_input':
            return self.get_components('phase_time_frequency_tab').inter_phase_delay_input
        if id == 'inter_stim_delay_input':
            return self.get_components('phase_time_frequency_tab').inter_stim_delay_input
        if id == 'phase_1_time_input':
            return self.get_components('phase_time_frequency_tab').phase_1_time_input
        if id == 'phase_2_time_input':
            return self.get_components('phase_time_frequency_tab').phase_2_time_input
        if id == 'channel_1_frequency_input':
            return self.get_components('phase_time_frequency_tab').channel_1_frequency_input

        if id == 'stimulation_graph_display':
            return self.get_components('stimulation_tabs').stimulation_graph_display

        print("missing id: ",id)
        return None

    def build(self):
        return MainWindow()

    def on_stop(self):
        '''Event handler for the `on_stop` event which is fired when the
        application has finished running (i.e. the window is about to be
        closed).
        '''
        self.thread = False

if __name__ == '__main__':
    kvloader = Builder.load_file("ui.kv")
    App = NeuroStimApp(kvloader)
    App.run()