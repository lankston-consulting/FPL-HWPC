#!/bin/bash
docker build --no-cache --target client -t hwpc-calc:client .
docker build --target worker -t hwpc-calc:worker . 
docker build --target base -t hwpc-calc:base .
docker build --target builder -t hwpc-calc:builder .