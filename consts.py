import math

SERIAL_COMMAND_INPUT_CHAR = '0000fe41-8e22-4541-9d4c-21edae82ed19'
FEEDBACK_CHAR = '0000fe42-8e22-4541-9d4c-21edae82ed19'
STREAM_READ_CHAR = '0000fe51-8e22-4541-9d4c-21edae82ed19'
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
UINT32_MAX = math.pow(2, 32) - 1
INTER_COMMAND_WAIT_TIME = 0.1 # seconds

class Parameters:
    start = bytearray(b'\x01\x00\x00\x00\x00')
    stop = bytearray(b'\x02\x00\x00\x00\x00')
    stim_type = bytearray(b'\x03')
    anodic_cathodic = bytearray(b'\x04')
    dac_phase_one = bytearray(b'\x05')
    dac_phase_two = bytearray(b'\x06')
    dac_gap = bytearray(b'\x07')
    phase_one_time = bytearray(b'\x08')
    inter_phase_gap = bytearray(b'\x09')
    phase_two_time = bytearray(b'\x0a')
    inter_stim_delay = bytearray(b'\x0b')
    inter_burst_delay = bytearray(b'\x0c')
    pulse_num = bytearray(b'\x0d')
    pulse_num_in_one_burst = bytearray(b'\x0e')
    burst_num = bytearray(b'\x0f')
    ramp_up = bytearray(b'\x10')
    short_electrode = bytearray(b'\x11')
    record_freq = bytearray(b'\x12')
    start_recording = bytearray(b'\x13\x00\x00\x00\x00')
    stop_recording = bytearray(b'\x14\x00\x00\x00\x00')
    electrode_voltage = bytearray(b'\x15\x00\x00\x00\x00')
    elec_offset = bytearray(b'\x16')
    show_dac = bytearray(b'\x17')
    return_idle = bytearray(b'\x18')
    check_state = bytearray(b'\x19\x00\x00\x00\x00')

    one_byte_padding = bytearray(b'\x00')
    two_byte_padding = bytearray(b'\x00\x00')