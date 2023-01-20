#!/bin/sh
# This tags a the latest hwpc-web:latest local container with the container
# registry information, and then pushes it to the registry. This requires
# AWS CLI to be set up and the AWS credential helper added to docker

# Beware of trying to authenticate docker to AWS when direnv is active. The
# environment variables that define the AWS service account will override
# personal AWS credentials, and authenticating docker will fail. Simply authenticate
# docker from a different location, or disable direnv
echo Tag and Push hwpc-web
docker tag hwpc-web:latest 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-web:latest
docker push 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-web:latest