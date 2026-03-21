import json
import urllib3
import boto3
import os
from datetime import date

http = urllib3.PoolManager()

# 🔐 READ TOKEN FROM ENV VARIABLE (SAFE)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# 🌍 MULTI-REGION LIST
regions = ['ap-south-1', 'us-east-1', 'us-west-2']

s3 = boto3.client('s3')
ce = boto3.client('ce', region_name='us-east-1')

# ---------------- SEND MESSAGE ----------------
def send_message(chat_id, text):
    url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    http.request(
        "POST",
        url,
        body=json.dumps({
            "chat_id": str(chat_id),
            "text": text
        }),
        headers={"Content-Type": "application/json"}
    )

# ---------------- RESOURCES (MULTI REGION) ----------------
def get_resources():
    total_ec2 = 0

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        instances = ec2.describe_instances()
        total_ec2 += sum(len(r['Instances']) for r in instances['Reservations'])

    buckets = s3.list_buckets()
    s3_count = len(buckets['Buckets'])

    return f"🌍 EC2 Instances (All Regions): {total_ec2}\nS3 Buckets: {s3_count}"

# ---------------- COST ----------------
def get_cost():
    today = date.today()
    start = today.replace(day=1)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': str(start),
            'End': str(today)
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )

    amount = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    return f"Current Month Cost: ${float(amount):.2f}"

# ---------------- CLEANUP (MULTI REGION) ----------------
def get_cleanup():
    total_unused = 0
    total_stopped = 0

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)

        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        total_unused += len(volumes['Volumes'])

        instances = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
        )
        total_stopped += sum(len(r['Instances']) for r in instances['Reservations'])

    return f"🌍 Unused EBS Volumes: {total_unused}\n🌍 Stopped EC2: {total_stopped}"

# ---------------- SMART SUGGESTIONS ----------------
def get_suggestions():
    suggestions = []
    total_unused = 0
    total_stopped = 0

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)

        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        total_unused += len(volumes['Volumes'])

        instances = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
        )
        total_stopped += sum(len(r['Instances']) for r in instances['Reservations'])

    if total_unused > 0:
        suggestions.append(f"⚠️ {total_unused} unused EBS volumes → delete to save cost")

    if total_stopped > 0:
        suggestions.append(f"⚠️ {total_stopped} stopped EC2 → terminate if not needed")

    if not suggestions:
        return "✅ No major optimization needed"

    return "\n".join(suggestions)

# ---------------- HANDLER ----------------
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        if 'message' not in body:
            return {"statusCode": 200}

        chat_id = body['message']['chat']['id']
        text = body['message'].get('text', '')

        if text == "/start":
            reply = "🌍 AWS Multi-Region Optimization Bot 🚀"

        elif text == "/help":
            reply = "/resources\n/cost\n/cleanup\n/report"

        elif text == "/resources":
            reply = get_resources()

        elif text == "/cost":
            reply = get_cost()

        elif text == "/cleanup":
            reply = get_cleanup() + "\n\n🧠 Suggestions:\n" + get_suggestions()

        elif text == "/report":
            reply = (
                "📊 AWS Smart Multi-Region Report\n\n"
                + get_resources() + "\n\n"
                + get_cost() + "\n\n"
                + get_cleanup() + "\n\n"
                + "🧠 Suggestions:\n"
                + get_suggestions()
            )

        else:
            reply = "Unknown command. Use /help"

        send_message(chat_id, reply)

        return {"statusCode": 200}

    except Exception as e:
        print("ERROR:", str(e))
        return {"statusCode": 200}