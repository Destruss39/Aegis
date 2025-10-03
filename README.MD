## Activate python virtual environment
venv\Scripts\Activate.ps1

## Run Qt Designer
venv\Scripts\pyqt6-tools.exe designer

## Convert .ui file to .py file
python -m PyQt6.uic.pyuic -x main_window.ui -o ui_main_window.py

## Build code to executable file
pyinstaller --onefile --windowed --icon=C:\Users\Dusti\Documents\development\padlock.ico main.py