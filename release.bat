@echo off

:: delete old files
::del /s /f /q "dist\olx\olx.exe"
del /s /f /q "dist\*"
del /s /f /q "olx.zip"

:: to EXE
pyinstaller --clean --noupx -n olx -y -i .\olx.ico .\car.py

:: Copy files
copy /v /b /y olx.ini .\dist\olx\
copy /v /b /y tlds-alpha-by-domain.txt .\dist\olx\

:: compact
"C:\ProgramData\chocolatey\bin\7z.exe" a olx.zip .\dist\olx\*
"C:\ProgramData\chocolatey\bin\7z.exe" a olx.zip olx.ini
"C:\ProgramData\chocolatey\bin\7z.exe" a olx.zip olx.ico
"C:\ProgramData\chocolatey\bin\7z.exe" a olx.zip tlds-alpha-by-domain.txt