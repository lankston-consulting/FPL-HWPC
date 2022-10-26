#!/bin/sh
echo Tag and Push hwpc-calc
docker tag hwpc-calc:latest 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:latest
docker push 234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:latest
