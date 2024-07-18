@echo off
for /f "delims=" %%i in ('python -c "import bigdl.cpp; print(bigdl.cpp.__file__)"') do set "cpp_file=%%i"
for %%a in ("%cpp_file%") do set "cpp_dir=%%~dpa"

set "cpp_dir=%cpp_dir:~0,-1%"
set "lib_dir=%cpp_dir%\libs"
set "destination_folder=%cd%"

pushd "%lib_dir%"
for %%f in (*) do (
    if not "%%f"=="ollama.exe" (
        mklink "%destination_folder%\%%~nxf" "%%~ff"
    )
)
popd

copy "%cpp_dir%\convert.py" .
copy "%cpp_dir%\convert-hf-to-gguf.py" .
xcopy /E /I "%cpp_dir%\gguf-py\" .\gguf-py
