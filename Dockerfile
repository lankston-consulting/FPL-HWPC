FROM python:3.10 AS builder
COPY . .
RUN pip install --upgrade pip
RUN pip install --upgrade build
RUN python -m build


FROM python:3.10 AS base
COPY --from=builder /dist/*.whl .
RUN pip install --no-cache-dir hwpccalc-*.whl
RUN pip freeze > requirements.txt
COPY ./src/ ./src/
COPY .env .env

 
FROM python:3.10 AS worker
EXPOSE 8786
EXPOSE 8787
ENTRYPOINT ["tini", "-g", "--"]


FROM base AS client
# COPY ./dist/hwpccalc-0.0.4-py3-none-any.whl ./hwpccalc-0.0.4-py3-none-any.whl
# RUN pip install --no-cache-dir ./hwpccalc-0.0.4-py3-none-any.whl
EXPOSE 8786
EXPOSE 8787
ENTRYPOINT ["python", "src/hwpccalc/main.py"]
