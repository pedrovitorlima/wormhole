# Use a Python image as base
FROM python:3.9-slim

WORKDIR /app

# Copy app files
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . . 

CMD ["python", "app.py"]
