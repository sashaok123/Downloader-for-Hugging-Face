@echo off

call venv\Scripts\activate.bat
python.exe lib/download-model.py %*
