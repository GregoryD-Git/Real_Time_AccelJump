@echo off
echo Activating dash environment...
call dash_env\Scripts\activate

echo Starting Dash app...
python Dash_plot_test_app.py

echo.
echo Dash app stopped.
pause