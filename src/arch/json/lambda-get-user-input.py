import json
import os
import urllib.parse

import boto3

print("Loading function")

s3 = boto3.client("s3")


def run_calculator_task(name, user_string):
    print("run_calculator_task:name", name)
    user_string = user_string.replace("hwpc-user-inputs/", "")
    user_string = user_string.replace("/user_input.json", "")
    print("run_calculator_task:user_string", user_string)
    # run a ECS fargate task
    client = boto3.client("ecs")
    response = client.run_task(
        cluster="hwpc-web-fargate-cluster",
        launchType="FARGATE",
        taskDefinition="calc-fargate-task",
        count=1,
        platformVersion="LATEST",
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [
                    "subnet-0094a0131c8b734cc",
                ],
                "securityGroups": [
                    "sg-086431530d4a3804d",
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
                        {"name": "AWS_CLUSTER_ARN", "value": os.getenv("AWS_CLUSTER_ARN")},
                        {"name": "AWS_SECURITY_GROUP", "value": os.getenv("AWS_SECURITY_GROUP")},
                        {"name": "AWS_SUBNET_ID", "value": os.getenv("AWS_SUBNET_ID")},
                        {"name": "AWS_VPC_ID", "value": os.getenv("AWS_VPC_ID")},
                        {"name": "DASK_N_WORKERS", "value": os.getenv("DASK_N_WORKERS")},
                        {"name": "HWPC__PURE_S3", "value": os.getenv("HWPC__PURE_S3")},
                        {"name": "HWPC__CDN_URI", "value": os.getenv("HWPC__CDN_URI")},
                        {"name": "HWPC__FIRST_RECYCLE_YEAR", "value": os.getenv("HWPC__FIRST_RECYCLE_YEAR")},
                        {"name": "HWPC__RECURSE_LIMIT", "value": os.getenv("HWPC__RECURSE_LIMIT")},
                        {"name": "S3_INPUT_BUCKET", "value": os.getenv("S3_INPUT_BUCKET")},
                        {"name": "S3_OUTPUT_BUCKET", "value": os.getenv("S3_OUTPUT_BUCKET")},
                    ],
                }
            ]
        },
    )
    print(response)


def lambda_handler(event, context):
    print("lambda_handler:event", event)
    # Get the object from the event and show its content type
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")
    print("lambda_handler:key", key)
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
        user_string = json_data["user_string"]
        run_calculator_task(name, user_string)
    except Exception as e:
        print(e)
        print(f"Error launching CALCULATOR task")
        raise e

    return 200
