FROM python:3.10.4

ENV PYTHONUNBUFFERED True

RUN python -m pip install --upgrade pip

# Set app directory
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . ./
ENV PORT ${PORT}

# EXPOSE ${PORT} 
EXPOSE 80
EXPOSE 443

# Run a WSGI server to serve the application. gunicorn must be declared as
# a dependency in requirements.txt.
ENTRYPOINT ["gunicorn", "-b", ":80", "--workers", "1", "--threads", "8", "--timeout", "0"]
CMD ["main:app"]