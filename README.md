# AWS Telegram Cloud Monitoring Bot

A Telegram bot that monitors AWS resources and gives basic insights on usage, cost, and unused services.

## Features
- Tracks EC2 instances across multiple regions  
- Shows total S3 buckets  
- Displays current monthly AWS cost  
- Identifies unused EBS volumes and stopped EC2 instances  
- Provides simple cost-saving suggestions  

## Tech Stack
Python, AWS Lambda, API Gateway, Boto3, Telegram Bot API

## Commands
- /resources – view EC2 and S3 resources  
- /cost – check current AWS cost  
- /cleanup – find unused resources  
- /report – full summary  

## Notes
The bot is designed to give a quick overview of AWS usage and highlight areas where costs can be reduced.