# Use a Python image as base
FROM python:3.9-slim

WORKDIR /app

# Copy app files
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the rest of the app files, including .env
COPY . . 

# Ensure .env is copied
COPY .env .env 

CMD ["python", "app.py"]