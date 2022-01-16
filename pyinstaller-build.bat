@echo off
python generate-version.py > _version.py
pyinstaller --clean --console --onefile --icon=NONE stuhealth.py
del _version.py
pause