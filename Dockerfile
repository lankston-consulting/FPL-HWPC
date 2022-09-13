FROM python:3.9.13

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /hwpccalc
WORKDIR $APP_HOME
COPY ./src/hwpccalc ./

# Install production dependencies.
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8786
EXPOSE 8787
