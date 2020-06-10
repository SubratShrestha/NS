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
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelStrip
from kivy.uix.popup import Popup
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import pprint

from kivy.config import Config
Config.set('graphics', 'width', 1024)
Config.set('graphics', 'height', 768)
Config.set('graphics', 'resizable', 'False')

"""Must be below config setting, otherwise it's reset"""
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from multiprocessing.connection import Listener, Client
import threading

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
]

def update_graph():
    graph = get_squarewave_plot()
    App.get_running_app().get_components('channel_1_stimulation_graph_display').add_widget(graph)

def get_squarewave_plot():
    t = np.linspace(0, 1, 500, endpoint=False)
    plt.plot(t, signal.square(2 * np.pi * 5 * t))
    plt.ylim(-2, 2)
    # plt.figure()
    return FigureCanvasKivyAgg(plt.gcf())

def update_graph_on_text_channel_1(instance, value):
    print(instance, value)
    update_graph()

def update_graph_on_toggle_channel_1(button,state):
    print(button.text, state)
    update_graph()

live_update_references = {
    'channel_1_stimulation_graph_display': [
        'termination_tabs_time_input_1',
        'termination_tabs_duty_cycle_input_1',
        'termination_tabs_time_input_1',
        'channel_1_output_current_input',
        'channel_1_cathodic_toggle',
        'channel_1_anodic_toggle',
        'channel_1_ramp_up_toggle',
        'channel_1_electrode_toggle',
        'channel_1_inter_burst_delay_input',
        'channel_1_burst_duration_input',
        'channel_1_inter_phase_delay_input',
        'channel_1_phase_time_input',
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


class BurstUniformStimulationTabs(TabbedPanel):
    pass


class TerminationTabs(TabbedPanel):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class AddDevicePopup(Popup):

    def BluetoothDiscoverLoop(self):
        self.ble_rv.data = App.get_running_app().device_data

    def Close(self):
        data = App.get_running_app().root.side_bar.device_rv.data

        for j in devices_dict.keys():
            adding = True
            for i in data:
                if i['text'] == j:
                    adding = False
            if adding and devices_dict[j]:
                App.get_running_app().root.side_bar.device_rv.data.append({'text': j})
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

class NeuroStimApp(App):
    def __init__(self, kvloader):
        super(NeuroStimApp, self).__init__()
        self.kvloader = kvloader
        self.device_data = []
        self.search = True
        self.t = threading.Thread(target=self.discover)
        self.t.start()

    def discover(self):
        address = ('localhost', 6000)
        listener = Listener(address, authkey=b'password')
        conn = listener.accept()
        while self.search:
            msg = conn.recv()
            if msg == 'close':
                conn.close()
                break
            else:
                self.device_data = msg
        listener.close()

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
        if id == 'stimulation_tabs':
            return self.get_components('device_settings').stimulation_tabs
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
            return self.get_components('channel_1_phase_time_frequency_tab').inter_phase_delay
        if id == 'channel_1_phase_time_input':
            return self.get_components('channel_1_phase_time_frequency_tab').phase_time
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
    kvloader = Builder.load_file("ui.kv")
    App = NeuroStimApp(kvloader)
    App.run()
