@echo off
pyinstaller --clean --console --onefile --icon=NONE --upx-exclude=vcruntime140.dll --runtime-hook=hook.py stuhealth-cli.py
pause