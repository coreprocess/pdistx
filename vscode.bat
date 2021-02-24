@echo off

code --extensions-dir=%~dp0.vscode-env/extensions --user-data-dir=%~dp0.vscode-env/userdata %*
