@echo off
setlocal

:menu
cls
echo.
echo  -------------------------------------------------
echo      WebP Packer/Unpacker Context Menu Installer
echo  -------------------------------------------------
echo.
echo  This script will modify the system-wide registry
echo  (HKEY_LOCAL_MACHINE) for all users.
echo.
echo  1. Install Context Menu (for All Users)
echo  2. Uninstall Context Menu (from All Users)
echo  3. Exit
echo.
set /p "choice=Enter your choice [1, 2, or 3]: "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto uninstall
if "%choice%"=="3" goto exit

echo Invalid choice. Please try again.
pause
goto menu

:install
cls
echo.
echo  -------------------------------------------------
echo           Install Context Menu
echo  -------------------------------------------------
echo.
echo Please provide the full path to your webp_packer.exe file.
echo Example: D:\Modding\Tools\wepb_packer\dist\webp_packer.exe
echo.
set /p "exePath=Enter the full path and press Enter: "

if not exist "%exePath%" (
    echo.
    echo ERROR: File not found at the specified path.
    echo Please make sure the path is correct and includes the filename.
    echo.
    pause
    goto menu
)

echo.
echo Installing context menu entries with path:
echo "%exePath%"
echo.

set "basekey=HKEY_LOCAL_MACHINE\SOFTWARE\Classes\AllFilesystemObjects\shell"
set "regkey_pack=%basekey%\WebpPack"
set "regkey_unpack=%basekey%\WebpUnpack"

reg add "%regkey_pack%" /ve /t REG_SZ /d "WebP Pack" /f
reg add "%regkey_pack%" /v "Icon" /t REG_SZ /d "%exePath%" /f
reg add "%regkey_pack%\command" /ve /t REG_SZ /d "cmd.exe /c \"\"%exePath%\" -p -s -r \"%1\"\"" /f

reg add "%regkey_unpack%" /ve /t REG_SZ /d "WebP Unpack" /f
reg add "%regkey_unpack%" /v "Icon" /t REG_SZ /d "%exePath%" /f
reg add "%regkey_unpack%\command" /ve /t REG_SZ /d "cmd.exe /c \"\"%exePath%\" -u -s -r \"%1\"\"" /f

echo.
echo Context menu entries installed successfully for all users.
pause
goto end

:uninstall
echo.
echo Uninstalling context menu entries...
echo.

set "basekey=HKEY_LOCAL_MACHINE\SOFTWARE\Classes\AllFilesystemObjects\shell"

reg delete "%basekey%\WebpPack" /f >nul 2>&1
reg delete "%basekey%\WebpUnpack" /f >nul 2>&1

echo.
echo Context menu entries uninstalled successfully from all users.
pause
goto end

:exit
exit

:end
endlocal
