# TODO: Generate Windows executables in setup script

import subprocess
import sys
from src.paths import Process

subprocess.run([sys.executable, Process.CONFIG])
