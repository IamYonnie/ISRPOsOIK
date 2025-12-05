@echo off
chcp 1251 > nul
cd /d C:\Kursach\Varyusha
call venv\Scripts\activate.bat
pip install --upgrade SQLAlchemy
python run.py
pause
