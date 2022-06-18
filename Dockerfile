FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 587

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--reload"]