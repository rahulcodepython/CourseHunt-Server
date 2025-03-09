# # Development
# # Use official Python image
# FROM python:3.13.1-alpine3.21

# WORKDIR /app

# COPY requirements.txt ./

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production
FROM python:3.13.1-alpine3.21

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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
COPY blogs ./blogs
COPY .env.prod .env
COPY manage.py .
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
