import subprocess
import sys

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'zmq'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy-stl'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scipy'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'imageio'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'matplotlib'])
