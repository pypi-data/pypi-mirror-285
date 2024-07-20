@echo off
for /f "delims=" %%i in ('python -c "import bigdl.cpp; print(bigdl.cpp.__file__)"') do set "cpp_file=%%i"
for %%a in ("%cpp_file%") do set "cpp_dir=%%~dpa"

set "cpp_dir=%cpp_dir:~0,-1%"
set "lib_dir=%cpp_dir%\libs"
set "source_path=%lib_dir%\ollama.exe"
set "target_path=%cd%\ollama.exe"
set "source_dist_dir=%lib_dir%\dist"
set "target_dist_dir=%cd%\dist"

mklink "%target_path%" "%source_path%" 
mklink /D "%target_dist_dir%" "%source_dist_dir%"
