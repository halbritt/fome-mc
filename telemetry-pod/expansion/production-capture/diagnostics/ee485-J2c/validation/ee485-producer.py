import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path
h = Path('telemetry-pod/expansion/production-capture')
subprocess.run([sys.executable, '-B', 'build/ee485-f8-record.py'],check=True)
subprocess.run([sys.executable, '-B', str(h/'build.py'), '/work/export', '--out', 'build/ee485-precheck-f8/capture'],check=True)
generated = ast.literal_eval(re.search(r'GENERATED = (\[.*?\])', (h/'build.py').read_text(), re.S).group(1))
for name in generated:
    shutil.copyfile(Path('build/ee485-precheck-f8/capture/composition')/name,h/'composition'/name)
shutil.copyfile('build/ee485-precheck-f8/capture/reconstruction.json',h/'reconstruction.json')
subprocess.run([sys.executable, '-B', str(h/'build.py'), '/work/export', '--check'],check=True)
