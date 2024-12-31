FROM python:3.11-slim

WORKDIR /app

COPY backend/src /app

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 80

# Set the default command to run the application
CMD ["uvicorn", "--port", "80", "--host", "0.0.0.0", "server:app"]
