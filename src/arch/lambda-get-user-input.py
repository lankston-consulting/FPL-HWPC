import json
import os
import urllib.parse

import boto3
from dotenv import load_dotenv

print("Loading function")

s3 = boto3.client("s3")

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

def runCalculatorTask(name, user_string):
    print(name)
    print(user_string)
    # run a ECS fargate task
    client = boto3.client("ecs")
    response = client.run_task(
        cluster="Calc-Fargate-Cluster",
        launchType="FARGATE",
        taskDefinition="calc-fargate-task",
        count=1,
        platformVersion="LATEST",
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [
                    "subnet-0a67a553e8d4a6e46",
                ],
                "securityGroups": [
                    "sg-013bca134dc371041",
                ],
                "assignPublicIp": "ENABLED",
            }
        },
        overrides={
            "containerOverrides": [
                {
                    "name": "hwpc-calc",
                    "command": [
                        "-p",
                        user_string,
                        "-n",
                        name,
                    ],
                    "environment": [
                        {"name": "AWS_ACCESS_KEY_ID", "value": AWS_ACCESS_KEY_ID},
                        {"name": "AWS_SECRET_ACCESS_KEY", "value": AWS_SECRET_ACCESS_KEY},
                        {"name": "S3_INPUT_BUCKET", "value": "hwpc"},
                        {"name": "S3_OUTPUT_BUCKET", "value": "hwpc_output"},
                    ],
                }
            ]
        },
    )
    print("HWPC Calc Client task requested. Response follows.")
    print(response)


def lambda_handler(event, context):
    print("event:", event)
    # Get the object from the event and show its content type
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(e)
        print(f"Error communicating with S3, {bucket}")
        raise e

    try:
        json_data = json.load(response["Body"])
    except Exception as e:
        print(e)
        print("Response:", response)
        print("Body:", response["Body"])
        print(f"Error decoding JSON")
        raise e

    try:
        name = json_data["scenario_name"]
        user_string = "hwpc-user-inputs/" + json_data["user_string"]
        # Uncomment this when we are going live with HWPC-Web
        runCalculatorTask(name, user_string)
    except Exception as e:
        print(e)
        print(f"Error launching CALCULATOR task")
        raise e
