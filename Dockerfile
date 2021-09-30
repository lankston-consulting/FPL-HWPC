FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY default_data/* default_data/
COPY hwpc/* hwpc/
COPY utils/* utils/

COPY __init__.py __init__.py
COPY config.py config.py
COPY hwpccalc.py hwpccalc.py
COPY main.py main.py

EXPOSE 8080

# ENTRYPOINT [ "python", "main.py" ]
CMD python main.py