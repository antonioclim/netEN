# FTP Scenario – NAT and firewall

## Objective
Understanding FTP limitations in modern networks with NAT and firewall.

## What happens
- the client communicates with the FTP server through a NAT
- active vs passive is tested
- where and why blockages can occur is observed

## What to observe
- who initiates the data connection
- what ports are used
- why passive mode is preferred

## Running
docker compose up --build

## Discussion
- why FTP is difficult to secure
- why SFTP/HTTPS are preferred
