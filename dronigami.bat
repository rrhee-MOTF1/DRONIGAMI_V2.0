@echo off
call DRONIGAMI_v1.0.0_ENV\Scripts\activate.bat
CD /D C:\DRONIGAMI_V2.0
python main.py
deactivate