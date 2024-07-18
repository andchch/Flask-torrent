FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends gcc &&  \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=runner.py
ENV FLASK_RUN_HOST=0.0.0.0

ENTRYPOINT ["flask", "run", "./flask_app.py"]