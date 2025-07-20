import os
import subprocess

HOST = os.environ.get('HOST', 8080)

clo = os.path.expanduser('~/AppData/Local/cloudpub/updates/clo.exe')
subprocess.run(f'{clo} publish http {HOST}')


