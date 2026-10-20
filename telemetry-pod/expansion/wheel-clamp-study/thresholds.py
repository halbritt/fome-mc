"""Conditional nominal circuit algebra; no diode or fault qualification."""
import json
from pathlib import Path

def model(ra,rb,rc,rg,cap):
    gain=rc/(ra+rb+rc)
    threshold=lambda vo:(3.3/56000+vo/100000)/(1/56000+1/100000+1/rg)
    # High output is loaded by its feedback branch: pull-up and feedback in series.
    high=(3.3/56000+3.3/104700)/(1/56000+1/104700+1/rg)
    rth=rc*(ra+rb)/(ra+rb+rc)
    return {'resistors_ohm':{'input_a':ra,'input_b':rb,'input_ground':rc,'threshold_ground':rg},'input_dc_load_ohm':ra+rb+rc,'signal_gain':gain,'clamp_attenuation':rc/(rb+rc),'input_thevenin_ohm':rth,'filter_capacitance_F':cap,'ideal_filter_tau_s':rth*cap,'falling_input_thresholds_after_isolation_diode_V':{str(vo):threshold(vo)/gain for vo in (0,.11,.55)},'rising_input_threshold_after_isolation_diode_V':high/gain,'high_output_voltage_V':3.3-(3.3-high)*4700/104700}
rows={'baseline':model(10000,0,10000,10000,220e-12),'same_loading_experiment':model(4000,12000,4000,3430,343.75e-12)}
rows['limitations']=['Ideal source, nominal resistances, ideal open collector high state, specified hypothetical low voltages.','Example resistor/capacitor values are not selected assembly parts.','Voltages are after the BAV199 isolation diode: no constant forward drop or connector-level threshold qualification assumed.','Small DC threshold shifts and different dynamic source impedance remain; diode loading is preserved only in the nominal DC no-clamp model.','No diode leakage, comparator input bias, tolerances, temperature, ground error or transient overshoot included.','Clamping current for 4k input resistor at -24V and hypothetical1V clamp is5.75mA, versus2.3mA in earlier10k example.']
Path(__file__).with_name('thresholds.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
