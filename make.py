import sys
import subprocess
import os
import shutil

subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def mkexec(name, script_name, consoled):
    subprocess.run([sys.executable, "-m", "PyInstaller", "-n", name, script_name, "--onefile",
                    "--console" if consoled else "--noconsole"])


mkexec("FolderToIso", "foldertoiso.py", False)
shutil.rmtree("build")
os.remove("FolderToIso.spec")
