#!/bin/sh 
echo Building hwpc-calc
pipenv run pipenv-setup sync
pipenv run python -m build
pipenv requirements > requirements.txt
docker build -t hwpc-calc:latest . 
docker tag hwpc-calc:latest 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:latest
# docker push 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:latest