@echo off

SET "EXE_PATH=D:\Modding\Tools\wepb_packer\dist\webp_packer.exe"



NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO =================================================================
    ECHO  Requesting Administrator Privileges...
    ECHO =================================================================
    ECHO.
    Powershell -Command "Start-Process '%~f0' -Verb RunAs"
    EXIT
)

:MENU
cls
echo.
echo ============================================================================
echo      WebP Packer/Unpacker Context Menu Manager
echo ============================================================================
echo.
echo   Using executable path: "%EXE_PATH%"
echo.
echo ----------------------------------------------------------------------------
echo.
echo   [1] Install Context Menu
echo   [2] Uninstall Context Menu
echo   [3] Exit
echo.
echo ----------------------------------------------------------------------------
echo.

CHOICE /C 123 /N /M "Enter your choice [1, 2, or 3]: "

IF ERRORLEVEL 3 GOTO :EXIT
IF ERRORLEVEL 2 GOTO :UNINSTALL
IF ERRORLEVEL 1 GOTO :INSTALL

:INSTALL
cls
echo.
echo ============================================================================
echo      INSTALLING CONTEXT MENU
echo ============================================================================
echo.

if NOT EXIST "%EXE_PATH%" (
    echo ERROR: File not found!
    echo Please edit this script and set the correct EXE_PATH.
    echo The current path is set to: "%EXE_PATH%"
    echo.
    GOTO :END
)

echo Adding "WebP Pack" entry...
reg add "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpPack" /v "" /t REG_SZ /d "WebP Pack" /f > nul
reg add "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpPack" /v "Icon" /t REG_SZ /d "%EXE_PATH%" /f > nul
reg add "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpPack\command" /v "" /t REG_SZ /d "cmd.exe /c \"\"%EXE_PATH%\" -p -s -r \"%%1\"\"" /f > nul

echo Adding "WebP Unpack" entry...
reg add "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpUnpack" /v "" /t REG_SZ /d "WebP Unpack" /f > nul
reg add "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpUnpack" /v "Icon" /t REG_SZ /d "%EXE_PATH%" /f > nul
reg add "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpUnpack\command" /v "" /t REG_SZ /d "cmd.exe /c \"\"%EXE_PATH%\" -u -s -r \"%%1\"\"" /f > nul

echo.
echo SUCCESS: Context menu entries have been installed.
echo.
GOTO :END

:UNINSTALL
cls
echo.
echo ============================================================================
echo      UNINSTALLING CONTEXT MENU
echo ============================================================================
echo.

echo Removing "WebP Pack" entry...
reg delete "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpPack" /f

echo Removing "WebP Unpack" entry...
reg delete "HKEY_CLASSES_ROOT\AllFilesystemObjects\shell\WebpUnpack" /f

echo.
echo SUCCESS: Context menu entries have been removed.
echo.
GOTO :END

:END
echo Press any key to return to the menu...
pause > nul
GOTO :MENU

:EXIT
