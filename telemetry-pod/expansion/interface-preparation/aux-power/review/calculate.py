import itertools,json
from pathlib import Path
r=(1050000,95300,287000);tol=.001+25e-6*100
out={'assumptions':{'resistor_fraction':tol,'temperature_range_C':[-40,125],'reference_temperature_C':25,'aging_allowance':0,'pin_leakage_A':1e-7}}
for typ,lo,hi in [('UVrise',1.18,1.23),('UVfall',1.09,1.135),('OVrise',1.18,1.23),('OVfall',1.09,1.135)]:
 vals=[]
 for s1,s2,s3,i,j,t in itertools.product([-1,1],[-1,1],[-1,1],[-1e-7,1e-7],[-1e-7,1e-7],[lo,hi]):
  a,b,c=[v*(1+s*tol) for v,s in zip(r,[s1,s2,s3])]
  vals.append(t*(1+a/(b+c))+i*a+j*a*c/(b+c) if typ.startswith('UV') else t*(1+(a+b)/c)+j*(a+b)+i*a)
 out[typ+'_V']=[min(vals),max(vals)]
a=r[0]*(1-tol);b=r[1]*(1-tol);c=r[2]*(1+tol)
out.update({'R1_min_ohm':a,'negative_fault_input_current_upper_A':(5.05+24)/a,'OVP_upper_if_UVLO_5V_V':5*c/(b+c)+1e-7*(r[1]*r[2]/(r[1]+r[2]))*(1+tol),'reference_initial_plus_fullspan_box_V':5*(.001+8e-6*165),'source_screening_min_V':5-5*(.001+8e-6*165)-.004,'planning_at_0.8ohm':{str(ma):{'switch_drop_V':ma*.001*.8,'remaining_lower_voltage_budget_V':.05-5*(.001+8e-6*165)-.004-ma*.001*.8} for ma in [25,40,152]}})
Path(__file__).with_name('calculations.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
