python -m pip install . --no-deps --ignore-installed --no-cache-dir -vvv
if errorlevel 1 exit 1

REM Add an menu entry for CoSApp
if not exist "%PREFIX%\Menu" mkdir "%PREFIX%\Menu"
if errorlevel 1 exit 1
copy "%RECIPE_DIR%\cosapp_lab.json" "%PREFIX%\Menu"
if errorlevel 1 exit 1
copy "%RECIPE_DIR%\CoSApp_lab.ico" "%PREFIX%\Menu"
if errorlevel 1 exit 1

