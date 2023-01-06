import json
import os
import urllib.parse

import boto3

print("Loading function")

s3 = boto3.client("s3")

# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def runCalculatorTask(name, user_string):
    print("runCalculatorTask:name", name)
    user_string = user_string.replace("hwpc-user-inputs/", "")
    user_string = user_string.replace("/user_input.json", "")
    print("runCalculatorTask:user_string", user_string)
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
                        {"name": "AWS_ACCESS_KEY_ID", "value": "X"},
                        {"name": "AWS_SECRET_ACCESS_KEY", "value": "X"},
                        {"name": "S3_INPUT_BUCKET", "value": os.getenv("S3_INPUT_BUCKET")},
                        {"name": "S3_OUTPUT_BUCKET", "value": os.getenv("S3_OUTPUT_BUCKET")},
                        {"name": "HWPC__PURE_S3", "value": os.getenv("HWPC__PURE_S3")},
                        {"name": "HWPC__CDN_URI", "value": os.getenv("HWPC__CDN_URI")},
                        {"name": "HWPC__FIRST_RECYCLE_YEAR", "value": os.getenv("HWPC__FIRST_RECYCLE_YEAR")},
                        {"name": "HWPC__RECURSE_LIMIT", "value": os.getenv("HWPC__RECURSE_LIMIT")},
                        # {"name": "HWPC__DEBUG__MODE", "value":"1"},
                        # {"name": "HWPC__DEBUG__START_YEAR", "value":"1990"},
                        # {"name": "HWPC__DEBUG__END_YEAR", "value":"2050"},
                        # {"name": "HWPC__DEBUG__PATH", "value":"t2023-01-03-01-2023T12:23:02"},
                        # {"name": "HWPC__DEBUG__NAME", "value":"t2023-01"},
                        {"name": "DASK_USE_FARGATE", "value": os.getenv("DASK_USE_FARGATE")},
                        {"name": "DASK_N_WORKERS", "value": os.getenv("DASK_N_WORKERS")},
                        {"name": "DASK_SCEDULER_CPU", "value": os.getenv("DASK_SCEDULER_CPU")},
                        {"name": "DASK_SCEDULER_MEM", "value": os.getenv("DASK_SCEDULER_MEM")},
                        {"name": "DASK_WORKER_CPU", "value": os.getenv("DASK_WORKER_CPU")},
                        {"name": "DASK_WORKER_MEM", "value": os.getenv("DASK_WORKER_MEM")},
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
        # Uncomment this when we are going live with HWPC-Web
        runCalculatorTask(name, user_string)
    except Exception as e:
        print(e)
        print(f"Error launching CALCULATOR task")
        raise e

    return 200
