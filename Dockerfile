FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY default_data/* default_data/
COPY hwpc/* hwpc/
COPY utils/* utils/

COPY __init__.py __init__.py
COPY config.py config.py
COPY hwpc-sa.json hwpc-sa.json
COPY main.py main.py

ENTRYPOINT [ "python", "main.py" ]