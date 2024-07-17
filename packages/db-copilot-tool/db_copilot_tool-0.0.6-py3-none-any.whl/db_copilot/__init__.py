import json
import os
import subprocess
import sys
import importlib
from db_copilot import lib

if sys.platform.startswith('win'):
    obfuscator_name = 'obfuscator.exe'
else:
    obfuscator_name = 'obfuscator'
exe_path = os.path.join(os.path.dirname(lib.__file__), obfuscator_name)
try:
    os.chmod(exe_path, 0o777)
except:
    print("Failed to chmod obfuscator, please chmod it manually")
cur_dir = os.path.dirname(__file__)
py_files = [os.path.join(cur_dir, f) for f in os.listdir(cur_dir) if f.endswith('.py')]
empty_py_files_with_encode = [f for f in py_files if os.path.exists(f + '.encode') and os.stat(f).st_size == 0]

for empty_py_file in empty_py_files_with_encode:
    module_name = '.' + os.path.basename(empty_py_file)[: -3]
    module = importlib.import_module(module_name, __package__)
    encode_path = empty_py_file + '.encode'
    output = subprocess.check_output([exe_path, encode_path], universal_newlines=True)
    output_json = json.loads(output)
    lib.O0OOO00OO00O0(module, output_json['a'], output_json['b'], output_json['c'])