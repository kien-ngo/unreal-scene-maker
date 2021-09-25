@ECHO off
setlocal enableDelayedExpansion

::Parse SETUP.json
set setup=
for /f "delims=" %%x in (SETUP.json) do set "setup=!setup!%%x"

rem Remove quotes
set setup=%setup:"=%
rem Remove braces
set "setup=%setup:~2,-2%"
rem Change colon+space by equal-sign
set "setup=%setup:: ==%"
rem Separate parts at comma into individual assignments
set "%setup:, =" & set "%"

::Get the project name from the first line of SETUP.txt
set projectname=%name%_%version%

::Set output path for where to save the created unreal project
set projectDirectory=%output%\\%projectname%
set projectPath=%projectDirectory%\\CustomMapDLC.uproject

:: Clear output folder if exists and create a new one 
IF EXIST %output% (
    rmdir %output% /s /q
)
md %output%

:: Clone template unreal project into output folder
IF EXIST %template% (
    xcopy /s /i %template% %projectDirectory% /Y
)

:: Rename Plugin Folder
set dlcName=DLC_%name%
set pluginPath=%projectDirectory%\\Plugins\\
set templatePlugin=%pluginPath%DLC_Scene
set newPlugin=%pluginPath%%dlcName%
ren %templatePlugin% %dlcName%
ren %newPlugin%\\DLC_Scene.uplugin %dlcName%.uplugin

echo %newPlugin%\\%dlcName%.uplugin

set enginepath=%engine:\\=\%

:: Fires python script to import datasmith
"%enginepath%" %projectPath% -run=pythonscript -script=%script%


pause