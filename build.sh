#!/bin/sh 
echo Building hwpc-calc
pipenv run pipenv-setup sync
pipenv run python -m build
pipenv requirements > requirements.txt
docker build -t hwpc-calc:worker-test dkr-worker.dockerfile
docker tag hwpc-calc:worker-test 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:worker-test
docker build -t hwpc-calc:client-test dkr-client.dockerfile
docker tag hwpc-calc:client-test 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:client-test
# docker push 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:latest