import math

def calculate_dac_value(phase_1_current, phase_2_current, vref_low, vref_high, anodic):
    step_voltage = float((vref_high - vref_low) / int(math.pow(2, 16) - 1))
    steps = int(3000 / step_voltage)
    dac_gap = steps / 2
    amp_step = 3000 / dac_gap
    if anodic:
        dac_phase_one = dac_gap - phase_1_current / amp_step
        dac_phase_two = dac_gap + phase_2_current / amp_step
        return int(dac_phase_one), int(dac_phase_two)
    else:
        dac_phase_one = dac_gap + phase_1_current / amp_step
        dac_phase_two = dac_gap - phase_2_current / amp_step
        return int(dac_phase_one), int(dac_phase_two)