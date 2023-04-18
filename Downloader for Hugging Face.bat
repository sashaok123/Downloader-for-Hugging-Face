@echo off

call venv\Scripts\activate.bat
pip install pywin32
pip install beautifulsoup4
python.exe download-model.py %*
pause