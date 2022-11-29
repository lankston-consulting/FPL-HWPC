FROM daskdev/dask:latest

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./dist/hwpccalc-0.0.4-py3-none-any.whl ./hwpccalc-0.0.4-py3-none-any.whl
RUN pip install --no-cache-dir ./hwpccalc-0.0.4-py3-none-any.whl
COPY ./src/ ./src/
COPY .env .env

ENTRYPOINT ["python", "src/hwpccalc/main.py"]
