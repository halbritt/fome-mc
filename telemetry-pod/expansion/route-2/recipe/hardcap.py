import pathlib,os,time,json,signal
pid=3889267;base=pathlib.Path('/home/halbritt/.cache/route-2-agent507');proc=pathlib.Path(f'/proc/{pid}');ticks=os.sysconf(os.sysconf_names['SC_CLK_TCK'])
if not proc.exists():raise SystemExit(0)
start=proc.joinpath('stat').read_text().rsplit(')',1)[1].split()[19];target=float(start)/ticks+1190
while proc.exists():
 try:
  fields=proc.joinpath('stat').read_text().rsplit(')',1)[1].split()
  if fields[19]!=start or fields[0]=='Z':break
  remaining=target-float(pathlib.Path('/proc/uptime').read_text().split()[0])
  if remaining>0:time.sleep(min(remaining,1));continue
  cmd=proc.joinpath('cmdline').read_bytes().replace(b'\0',b' ').decode();assert str(base/'run') in cmd and 'py_router/route.py' in cmd and os.getpgid(pid)==pid
  elapsed=float(pathlib.Path('/proc/uptime').read_text().split()[0])-float(start)/ticks
  os.killpg(pid,signal.SIGTERM);base.joinpath('hardcap.json').write_text(json.dumps({'backend_pid':pid,'signal':'SIGTERM process group','elapsed_s':elapsed,'reason':'1,000 second soft stop was not honored; enforce owner 1,200 second total backend limit with ten second termination margin'},indent=2));print('hardcap sent',elapsed,flush=True);break
 except FileNotFoundError:break
