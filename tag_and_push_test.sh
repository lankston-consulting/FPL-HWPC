#!/bin/sh
echo Tag and Push hwpc-calc
docker tag hwpc-calc:worker 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:worker
docker push 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:worker
