#!/bin/sh 
echo Building hwpc-calc
pipenv requirements > requirements.txt
docker build -t hwpc-calc:test . 
docker tag hwpc-calc:test 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:test
# docker push 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:test