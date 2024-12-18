FROM python:3.13.1-alpine3.21

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project files
COPY authentication ./authentication
COPY course ./course
COPY feedback ./feedback
COPY server ./server
COPY templates ./templates
COPY transactions ./transactions
COPY .env .
COPY manage.py .

ENV ENVIRONMENT=production

RUN python manage.py collectstatic --noinput
