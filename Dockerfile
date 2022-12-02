FROM python:3.10.4 AS builder
ENV PYTHONBUFFERED 1

# Set app directory
ENV PKG_HOME /hwpccalc
WORKDIR $PKG_HOME

COPY ./src/* src/
COPY ./pyproject.toml .
COPY ./setup.py .

RUN pip install --upgrade build pip 
RUN python -m build
# RUN pip install .

#########################################################

FROM python:3.10.4 AS base
ENV PYTHONBUFFERED 1

RUN pip install --upgrade pip wheel

COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENV PKG_HOME /hwpccalc
COPY --from=builder $PKG_HOME/dist/hwpccalc-*.whl .
RUN pip install --no-cache-dir hwpccalc-*.whl

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

COPY .env .env

#########################################################

FROM base AS worker
ENV PYTHONBUFFERED 1

EXPOSE 8786
EXPOSE 8787
ENTRYPOINT ["/tini", "-g", "--"]

#########################################################

FROM base AS client
ENV PYTHONBUFFERED 1

# Set app directory
COPY ./src/hwpccalc/main.py main.py
EXPOSE 8786
EXPOSE 8787
EXPOSE 8080
# ENTRYPOINT ["python", "main.py"]
ENTRYPOINT ["/tini", "-g", "--", "python"]
