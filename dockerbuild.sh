#!/bin/bash
docker build --no-cache --target client --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:client .
docker build --target worker --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:worker . 
docker build --target base -t hwpc-calc:base .
docker build --target builder -t hwpc-calc:builder .