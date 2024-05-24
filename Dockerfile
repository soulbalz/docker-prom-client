from python:3.11-alpine

workdir /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY main.py main.py

CMD ["python", "main.py"]
