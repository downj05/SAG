@echo off
echo "creating new venv..."
python -m venv Script\venv
echo "installing requirements..."
Script\venv\Scripts\pip install -r Script\requirements.txt
echo "setting version cache to latest..."
Script\venv\Scripts\python.exe update.py --set
echo "done"
pause