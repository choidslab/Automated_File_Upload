import sys
from cx_Freeze import setup, Executable

setup(  name = "Autouploader",
        version = "1.1",
        description = "Auotoupload",
        author = "Dooseop Choi",
        executables = [Executable("./AutoUpload_multi.py")])
