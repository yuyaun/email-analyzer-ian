FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV CRON_JOB=true
ENV CONSUMER=true
CMD ["python", "-m", "uvicorn", "app.main:app", "--reload"]
