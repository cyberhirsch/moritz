@echo off
rem Gentle Moritz build: low priority, 2 MSBuild jobs, 2 compiler threads each.
rem Usage: build_gentle.cmd [Release|Debug|RelWithDebInfo]  (default Release; Debug installs to bin\Debug)
set CONFIG=%1
if "%CONFIG%"=="" set CONFIG=Release
set LOG=G:\Code\Moritz\build.log
if not "%CONFIG%"=="Release" set LOG=G:\Code\Moritz\build_%CONFIG%.log
set CL=/MP2
cmake --build G:\Code\Moritz\build_windows_Full_x64_vc17_Release --config %CONFIG% --target install -- /m:2 /nologo /v:m > %LOG% 2>&1
echo EXIT %ERRORLEVEL% >> %LOG%
