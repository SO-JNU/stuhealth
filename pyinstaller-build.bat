@echo off
python generate-version.py > _version.py
pyinstaller --clean --console --onefile --icon=NONE --upx-exclude=vcruntime140.dll --hidden-import=_version stuhealth-cli.py
del _version.py
pause