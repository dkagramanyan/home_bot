@echo off
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
wsl -e bash -c "cd; ./jupyterhub_start.sh"