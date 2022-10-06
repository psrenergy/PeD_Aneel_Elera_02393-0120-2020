@echo off

SET CURR_DIR="%~dp0"
SET OPEN_BROWSER=%1
SET CASE_PATH=%~2
SET CASE_FORMAT=%3
SET SDDP_PATH="%~2\SDDP"

:: Change directory
cd /d %CURR_DIR%

:: Run Converter
IF "%CASE_FORMAT%"== "-nw" (
	if not exist "%CASE_PATH%\SDDP" MKDIR "%CASE_PATH%\SDDP"
	pushd NWSDDP
    nwsddp.exe -NW:"%CASE_PATH%" -SP:%SDDP_PATH%
    popd

    IF "%OPEN_BROWSER%"=="-browser" (
    START R-Portable\App\R-Portable\bin\Rscript.exe --vanilla --slave runHydroCheck_browser.R %SDDP_PATH%
	) ELSE (
    START R-Portable\App\R-Portable\bin\Rscript.exe --vanilla --slave runHydroCheck.R %SDDP_PATH%
	)

) ELSE (
    :: Run HydroCheck
	IF "%OPEN_BROWSER%"=="-browser" (
	    START R-Portable\App\R-Portable\bin\Rscript.exe --vanilla --slave runHydroCheck_browser.R "%CASE_PATH%"
	) ELSE (
	    START R-Portable\App\R-Portable\bin\Rscript.exe --vanilla --slave runHydroCheck.R "%CASE_PATH%"
	)
)
