@echo off
echo === Building Agy Helper for Windows ===

python -m pip install --upgrade pip
python -m pip install pyinstaller pycairo PyGObject

pyinstaller --clean agy_helper.spec

echo Build complete! Windows executable is located at dist\AgyHelper.exe
pause
