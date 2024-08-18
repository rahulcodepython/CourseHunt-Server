FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend

COPY requirements.txt /backend/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /backend/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000