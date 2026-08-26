"""Run ngrok tunnel for public URL access to Flask application."""
import os
import subprocess
import sys
import time
from pyngrok import ngrok

PYTHON_EXECUTABLE = sys.executable
with subprocess.Popen([PYTHON_EXECUTABLE, 'app.py'], cwd=os.getcwd()) as process:
	tunnel = ngrok.connect(5000)
	print(tunnel.public_url)
	sys.stdout.flush()

	# Keep the process alive so the tunnel stays open.
	time.sleep(3600)
