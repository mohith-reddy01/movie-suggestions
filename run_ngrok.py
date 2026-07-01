import os
import subprocess
import sys
import time
from pyngrok import ngrok

python_executable = sys.executable
subprocess.Popen([python_executable, 'app.py'], cwd=os.getcwd())

tunnel = ngrok.connect(5000)
print(tunnel.public_url)
sys.stdout.flush()

# Keep the process alive so the tunnel stays open.
time.sleep(3600)
