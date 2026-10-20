import json,itertools,math
from pathlib import Path
# Guardband2.4..2.586 V is a declared planning envelope, not a full DC error guarantee.
t=.0035;elo,ehi=2.4,2.586;rs=474;rp=10000;mon=1501990
vfmax=4.95-ehi-rs*(1+t)*(.001+4*ehi/(rp*(1-t))+ehi/mon)
d={'resistor_fraction':t,'excitation_planning_guardband_V':[elo,ehi],'diode_max_V_for_1mA_allshort':vfmax,'allshort_shunt_mA_at_VF1p3':1000*((4.95-1.3-ehi)/(rs*(1+t))-4*ehi/(rp*(1-t))-ehi/mon)}
for source in [5.05,6.4,16,24]:
 points=[]
 for er,sa,sb,sp in itertools.product([elo,ehi],[-1,1],[-1,1],[-1,1]):
  ra=237*(1+sa*t);rb=237*(1+sb*t);pull=rp*(1+sp*t);ib=(source-er)/(ra+rb);ish=ib+4*(24-er)/pull
  points.append((ish,ish*er,ib*ib*ra,ib*ib*rb))
 d[f'source{source}_allfour24V_zero_diode_drop']={'max_shunt_mA':1000*max(x[0] for x in points),'max_shunt_W':max(x[1] for x in points),'max_each_bias_W':max(max(x[2:]) for x in points)}
d['CRCW2512_1W70C_derated_W']={str(a):(155-a)/85 for a in [85,105,125]}
d['NTC_nominal_2p495V']={'maximum_self_heat_W':2.495**2/(4*10000*1.5),'resistance_at_max_power_ohm':10000/1.5,'open_input_V':2.495*2/3,'10k_input_V':2.495*.4,'open_ADC_codes_at5Vref':4096*2.495*2/3/5,'10k_ADC_codes_at5Vref':4096*2.495*.4/5,'tau_max_s':(10000*20000/30000)*100e-9,'fullscale_halfLSB_settle_s':math.log(8192)*(10000*20000/30000)*100e-9}
d['diagnostic_10conversions_screen_ms']=1000*(10*162/400000+4*1061/(1024000*.98))
d['LM4040_3V_330_bias_6p4_source_four16_mA']=1000*((6.4-2.9449)/(330*(1-t))+4*(16-2.9449)/(10000*(1-t)))
tb=.01+100e-6*(155-25)
d['alternative_bias_1pct_100ppm_through155C']={'bias_resistor_fraction':tb,'VFmax_for_1mA':4.95-ehi-rs*(1+tb)*(.001+4*ehi/(rp*(1-t))+ehi/mon),'allshort_shunt_mA_at_VF1p3':1000*((4.95-1.3-ehi)/(rs*(1+tb))-4*ehi/(rp*(1-t))-ehi/mon),'each_bias_max_W_at24V':(24-elo)**2/(4*237*(1-tb)),'max_shunt_mA_at24V':1000*((24-elo)/(rs*(1-tb))+4*(24-elo)/(rp*(1-t)))}
rs=400;tb=(1+.01)*(1+100e-6*130)-1;t=(1+.001)*(1+25e-6*130)-1;mon=1501990*(1-t)
new={'bias_resistor_fraction':tb,'VFmax_for_1mA':4.95-ehi-rs*(1+tb)*(.001+4*ehi/(rp*(1-t))+ehi/mon),'allshort_shunt_mA_at_VF1p5':1000*((4.95-1.5-ehi)/(rs*(1+tb))-4*ehi/(rp*(1-t))-ehi/mon),'HP_1p5W70C_derated_W':{str(a):1.5*(155-a)/85 for a in [85,105,125]}}
for source,fault in [(5.05,16),(6.4,16),(16,16),(24,24)]:
 imax=(source-elo)/(rs*(1-tb))+4*(fault-elo)/(rp*(1-t))
 psh=ehi*((source-ehi)/(rs*(1-tb))+4*(fault-ehi)/(rp*(1-t)))
 new[f'AUX{source}_four_signal{fault}']={'max_shunt_mA':1000*imax,'max_shunt_W':psh,'max_each_bias_W':(source-elo)**2/(4*200*(1-tb)),'max_each_pullup_W':(fault-elo)**2/(rp*(1-t)),'theta_shunt_max_KperW_for105ambient150junction':45/psh}
d['selected_two200ohm_HP_candidate']=new
Path(__file__).with_name('calculations.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
