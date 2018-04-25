import sys
from cx_Freeze import setup, Executable

setup(  name = "Autoupload",
        version = "1.0",
        description = "Auotoupload",
        author = "dschoi",
        executables = [Executable("./AutoUpload.py")])
