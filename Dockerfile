FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=runner.py
ENV FLASK_RUN_HOST=0.0.0.0

#RUN flask db upgrade

CMD ["flask", "run"]