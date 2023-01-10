#!/bin/bash
direnv reload
# docker build --no-cache --target client --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:client .
docker build --target client --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:client .
docker build --target worker --build-arg PY_VERSION=${PY_VERSION} -t hwpc-calc:worker . 
