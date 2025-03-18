@echo off
CD /D C:\DRONIGAMI_V2.0
call DRONIGAMI_v1.0.0_ENV\Scripts\activate.bat
python main.py
deactivate