FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

ENV PYTHONPATH "/code/app"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
