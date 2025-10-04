## Activate python virtual environment
venv\Scripts\Activate.ps1

## Build code to executable file
pyinstaller app.py --onefile --windowed --add-data "index.html;." --add-data "script.js;."