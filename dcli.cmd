@echo off
rem dcli - canonical CLI shim. Forwards to agent_cli.py at this script's directory.
rem Preserves cwd so agent_cli.py reads the right project.json.
python "%~dp0agent_cli.py" %*
