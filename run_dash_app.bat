@echo off
echo Activating dash environment...
call dash_env\Scripts\activate

echo Starting Dash app...
python RT_jump_app.py

echo.
echo Dash app stopped.
pause