@echo off
setlocal enabledelayedexpansion

:: Define paths
set "source_folder=C:\MEDIANSI\MediCare"
set "target_folder=C:\MEDIANSI\MediCare\CSV"
set "config_file=F:\Medibot\json\config.json"
set "python_script=C:\Python34\Lib\site-packages\MediBot\update_json.py"
set "python_script2=C:\Python34\Lib\site-packages\MediBot\Medibot.py"
set "medicafe_package=medicafe"
set "upgrade_medicafe=F:\Medibot\update_medicafe.py"
set "temp_file=F:\Medibot\last_update_timestamp.txt"
set "firefox_path=C:\Program Files\Mozilla Firefox\firefox.exe"
set "claims_status_script=..\MediLink\MediLink_ClaimStatus.py"
set "deductible_script=..\MediLink\MediLink_Deductible.py"
set "package_version="
set PYTHONWARNINGS=ignore

:: Check if Python is installed and the path is correctly set
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to PATH.
    exit /b
)

:: Check if the MediCafe package is installed and retrieve its version
echo Checking for installed MediCafe package version...
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" > temp.txt 2>nul
set /p package_version=<temp.txt
del temp.txt

if not defined package_version (
    echo MediCafe package version not detected or MediCafe not installed. Consider manual re-install.
    exit /b
)

:: Extract version number and display it
for /f "tokens=2 delims==" %%a in ("%package_version%") do (
    set "medicafe_version=%%a"
)

if not defined medicafe_version (
    echo Failed to detect MediCafe version.
) else (
    echo Detected MediCafe version: %medicafe_version%
)

:: Check for internet connectivity
ping -n 1 google.com > nul 2>&1
if %ERRORLEVEL% neq 0 (
    set "internet_available=0"
    echo No internet connection detected.
) else (
    set "internet_available=1"
    echo Internet connection detected.
)

:: Common pre-menu setup
echo Setting up the environment...
if not exist "%config_file%" (
    echo Configuration file missing.
    goto end_script
)

:: Check if the file exists and attempt to move it
:: Implementing a check with copy as a fallback if move fails
echo Checking for the upgrade script...
if exist "C:\Python34\Lib\site-packages\MediBot\upgrade_medicafe.py" (
    echo Found upgrade_medicafe.py. Attempting to move...
    move "C:\Python34\Lib\site-packages\MediBot\upgrade_medicafe.py" "F:\Medibot\upgrade_medicafe.py" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Move failed. Attempting copy and delete as fallback...
        copy "C:\Python34\Lib\site-packages\MediBot\upgrade_medicafe.py" "F:\Medibot\upgrade_medicafe.py" >nul 2>&1
        if %errorlevel% neq 0 (
            echo Copy failed. Error Level: %errorlevel%
        ) else (
            del "C:\Python34\Lib\site-packages\MediBot\upgrade_medicafe.py" >nul 2>&1
            if %errorlevel% neq 0 (
                echo Delete failed. Manual cleanup may be required.
            ) else (
                echo File copied and original deleted successfully.
            )
        )
    ) else (
        echo File moved successfully.
    )
) else (
    echo upgrade_medicafe.py not detected. Check path and filename.
)

:: Main menu
:main_menu
cls
echo version: %medicafe_version%
echo --------------------------------------------------------------
echo                .//*  Welcome to MediCafe  *\\. 
echo --------------------------------------------------------------
echo. 
echo Please select an option:
if "!internet_available!"=="1" (
    echo 1. Check for MediCafe Package Updates
    echo 2. Download Email de Carol
    echo 3. MediLink Claims
    echo 4. United Claims Status
    echo 5. United Deductible
)
echo 6. Run MediBot
echo 7. Exit
echo.
set /p choice=Enter your choice:  

if "!choice!"=="7" goto end_script
if "!choice!"=="6" goto medibot_flow
if "!choice!"=="5" goto united_deductible
if "!choice!"=="4" goto united_claims_status
if "!choice!"=="3" goto medilink_flow
if "!choice!"=="2" goto download_emails
if "!choice!"=="1" goto check_updates

:: Medicafe Update
:check_updates
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
echo Checking for MediCafe package updates. Please wait...
start cmd /c py "%upgrade_medicafe%" > upgrade_log.txt 2>&1 && (
    echo %DATE% %TIME% Upgrade initiated. >> "%temp_file%"
    echo Exiting batch to complete the upgrade.
) || (
    echo %DATE% %TIME% Update failed. Check logs. >> upgrade_log.txt
)
exit /b

:: Download Carol's Emails
:download_emails
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
echo Downloading emails...
:: move this path.
py "../MediLink/MediLink_Gmail.py" "%firefox_path%"
if errorlevel 1 (
    echo Failed to download emails.
    pause
) else (
    echo Calling CSV Processor...
    call :process_csvs
)
goto main_menu

:: Run MediBot Flow
:medibot_flow
call :process_csvs
cls
echo Please wait...
py "%python_script2%" "%config_file%"
if errorlevel 1 echo Failed to run MediBot.
pause
goto main_menu

:: Continue to MediLink
:medilink_flow
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
call :process_csvs
cls
:: move this path.
py "C:\Python34\Lib\site-packages\MediLink\MediLink.py"
if errorlevel 1 echo MediLink failed to execute.
pause
goto main_menu

:: United Claims Status
:united_claims_status
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
cls
echo Checking United Claims Status...
py "%claims_status_script%"
if errorlevel 1 echo Failed to check United Claims Status.
pause
goto main_menu

:: United Deductible
:united_deductible
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
cls
echo Checking United Deductible...
py "%deductible_script%"
if errorlevel 1 echo Failed to check United Deductible.
pause
goto main_menu

:: Process CSV Files
:process_csvs
for /f "tokens=1-5 delims=/: " %%a in ('echo %time%') do (
    set "hour=%%a"
    set "minute=%%b"
    set "second=%%c"
)
for /f "tokens=2-4 delims=/ " %%a in ('echo %date%') do (
    set "day=%%a"
    set "month=%%b"
    set "year=%%c"
)
set "timestamp=!year!!month!!day!_!hour!!minute!"

set "latest_csv="
for /f "delims=" %%a in ('dir /b /a-d /o-d "%source_folder%\*.csv" 2^>nul') do (
    set "latest_csv=%%a"
    echo Found New CSV Files...
    goto process_found_csv
)
::echo CSV Check Complete.
goto :eof

:process_found_csv
echo Processing CSVs...
move "%source_folder%\!latest_csv!" "%target_folder%\SX_CSV_!timestamp!.csv"
set "new_csv_path=%target_folder%\SX_CSV_!timestamp!.csv"
py "%python_script%" "%config_file%" "!new_csv_path!"
echo CSV Processor Complete...
goto :eof

:: Exit Script
:end_script
echo Exiting MediCafe.
pause
exit /b
