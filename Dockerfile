#FROM python:3.12-slim
#ENV PYTHONDONTWRITEBYTECODE=1
#COPY migrate-entrypoint.sh /app/migrate-entrypoint.sh
# make it executable inside the container
#RUN ["chmod", "+x", "/app/migrate-entrypoint.sh"]
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt 
#COPY . .
#EXPOSE 8000
#CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000", "--workers", "2"]
#CMD ['uvicorn',"main:app" ,"--host","0.0.0.0","--port","8000"]


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Install netcat
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY migrate-entrypoint.sh /app/migrate-entrypoint.sh
RUN chmod +x /app/migrate-entrypoint.sh

COPY . .

EXPOSE 8000
