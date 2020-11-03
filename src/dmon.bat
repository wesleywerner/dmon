@echo off
REM set your PATH to include this directory to use dmon from any other.
REM requires Python in your path.
REM (%~dp0) translates to the directory where this bat file lives.
python %~dp0\dmon.py %*
