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
# RUN echo "$USER_BUCKET"
# RUN echo "$NAME"



# ENV -p "$USER_BUCKET"
# ENV -n "$NAME"

# ARG name
# ARG user_string

# ENV NAME $name
# ENV USER_BUCKET $user_string

# RUN echo $NAME
# RUN echo $USER_BUCKET



ENTRYPOINT ["python"]
CMD ["src/hwpccalc/main.py", "-p", "hwpc-user-inputs/0b849568-2ea5-46ed-aed2-1f2382ce528f", "-n", "cali2"]
