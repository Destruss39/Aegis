## Activate python virtual environment
venv\Scripts\Activate.ps1

## Build code to executable file
pyinstaller app.py --onefile --windowed --icon=C:\Users\Dusti\Documents\development\padlock.ico --add-data "index.html;." --add-data "script.js;." --add-data "style.css;."