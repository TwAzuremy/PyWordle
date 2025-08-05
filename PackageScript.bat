@echo off
setlocal enabledelayedexpansion

:: Config 
set APP_NAME=PyWordle
set MAIN_SCRIPT=main.py
set ICON_FILE=icon.ico
set BUILD_DIR=build
set DIST_DIR=dist

:: Included catalogs
set DIRS_TO_ADD=config error game lang ui utils

:: Generate add-data parameters 
set ADD_DATA_CMD=
for %%d in (%DIRS_TO_ADD%) do (
    set "ADD_DATA_CMD=!ADD_DATA_CMD! --add-data "%%d;%%d""
)

:: Packing instructions 
echo Packing %APP_NAME%...
pyinstaller --onefile ^
    --name %APP_NAME% ^
    --icon %ICON_FILE% ^
    --workpath %BUILD_DIR% ^
    --distpath %DIST_DIR% ^
    --specpath . ^
    %ADD_DATA_CMD% ^
    %MAIN_SCRIPT%

:: Clean up temporary files
echo Cleaning up temporary files...

echo Packing is complete!
echo The program is saved to: %DIST_DIR%\%APP_NAME%.exe
pause