FROM python:3.12-slim
LABEL version="1.0"
LABEL authors="emanuel_brea"
LABEL description="Opening generator"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./opening_generator /code/opening_generator
COPY ./config.toml /code/config.toml

CMD ["uvicorn", "opening_generator.application:app", "--host", "0.0.0.0", "--port", "80"]