import math


def calculate_dac_value(phase_1_current, phase_2_current, vref_low, vref_high, anodic):
    step_voltage = float((vref_high - vref_low) / int(math.pow(2, 12) - 1))
    steps = int(3000 / step_voltage)
    dac_gap = steps / 2
    amp_step = 3000 / dac_gap
    if anodic:#phase 1 is negative
        dac_phase_one = phase_1_current
        dac_phase_two = phase_2_current
        return int(dac_phase_one), int(dac_phase_two)
    else:
        dac_phase_one = phase_1_current
        dac_phase_two = phase_2_current
        return int(dac_phase_one), int(dac_phase_two)


def calculate_adv_to_mv(adc_value):
    adc = int(adc_value)
    pos = adc >= int(4096 / 2)
    if pos:
        voltage = int(float(float(adc - float(4096 / 2)) / float(4096 / 2)) * 18000)
        return int(voltage)
    else:
        adc += 2048
        voltage = int(float(float(adc - float(4096 / 2)) / float(4096 / 2)) * 18000)
        return int(-1*int(18000-voltage))
