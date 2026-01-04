# FTP Scenario – control vs data

## Objective
Understanding FTP operation mode by observing the separation between:
- control connection
- data connection

## What happens
- runs a real FTP server (pyftpdlib)
- a Python FTP client connects
- executes LIST, STOR, RETR
- compares passive vs active mode

## What to observe
- ports used
- when data connections appear
- difference between PASV and PORT

## Running
docker compose up --build

## Questions
- Why do two connections exist?
- Why is active mode problematic?
