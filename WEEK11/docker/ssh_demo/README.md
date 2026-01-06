# SSH Scenario – simple provisioning

## Objective
Using SSH as a general control and automation mechanism.

## What happens
- a Python controller reads a JSON plan
- connects via SSH
- executes commands
- transfers files

## What to observe
- SSH as a control protocol
- multiple channels over a connection
- similarity with real DevOps tools

## Running
docker compose up --build

## Discussion
- what makes SSH so versatile
- why many tools rely on SSH
