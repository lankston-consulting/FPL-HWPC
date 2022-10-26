# FROM daskdev/dask:latest

# COPY requirements.txt requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir dask-cloudprovider[aws]

# COPY ./dist/hwpccalc-0.0.2-py3-none-any.whl ./hwpccalc-0.0.2-py3-none-any.whl
# RUN pip install --no-cache-dir ./hwpccalc-0.0.2-py3-none-any.whl

# COPY .env .env
# # COPY ./data /data
# # COPY ./default_data /default_data

# ENTRYPOINT ["tini", "-g", "--"]


FROM daskdev/dask:latest

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir dask-cloudprovider[aws]

COPY ./dist/hwpccalc-0.0.2-py3-none-any.whl ./hwpccalc-0.0.2-py3-none-any.whl
RUN pip install --no-cache-dir ./hwpccalc-0.0.2-py3-none-any.whl
COPY ./src/ ./src/
COPY .env .env

# ARG NAME
# ARG USER_BUCKET

# ENV -n=$NAME
# ENV -p=$USER_BUCKET


CMD ["src/hwpccalc/main.py", $USER_BUCKET, $NAME]
ENTRYPOINT ["python"]