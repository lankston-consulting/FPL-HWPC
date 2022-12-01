FROM python:3.10.4 AS builder
COPY . .
RUN pip install --upgrade pip
RUN pip install --upgrade build wheel
RUN python -m build


FROM python:3.10.4 AS base
COPY --from=builder /dist/*.whl .
RUN pip install --no-cache-dir hwpccalc-*.whl
COPY ./src/ ./src/
COPY .env .env


FROM base AS worker
EXPOSE 8786
EXPOSE 8787
ENTRYPOINT ["tini", "-g", "--"]


FROM base AS client
EXPOSE 8786
EXPOSE 8787
ENTRYPOINT ["python", "src/hwpccalc/main.py"]
