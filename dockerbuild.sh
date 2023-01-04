#!/bin/bash
direnv reload
docker build --no-cache --target client --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:client .
docker build --target worker --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:worker . 
docker build --target base --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:base .
docker build --target builder --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:builder .