@ECHO off
mkdir "profiles"
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"

set "timestamp=%YYYY%%MM%%DD%%HH%%Min%%Sec%"
set "output=profiles/%timestamp%.prof"
echo %output%
python -m cProfile -o %output% run.py