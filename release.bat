@echo off

:: delete old files
rmdir /s /q ".\__pycache__\"
rmdir /s /q ".\Output\"
rmdir /s /q ".\build\"
del /s /f /q ".\olx.zip"

:: to EXE
python.exe .\setup.py build

:: Copy files
copy /v /b /y olx.ini .\build\exe.win-amd64-3.8\
copy /v /b /y tlds-alpha-by-domain.txt .\build\exe.win-amd64-3.8\

:: to Zip
7z.exe a olx.zip .\build\exe.win-amd64-3.8\*
7z.exe a olx.zip olx.ico

:: Installer
ISCC.exe .\olx.iss