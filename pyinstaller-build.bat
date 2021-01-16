@echo off
pyinstaller --clean --console --onefile --icon=NONE --upx-exclude=vcruntime140.dll stuhealth-cli.py
pause