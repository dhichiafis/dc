FROM python3:12-slim

ENV PYTHONDONTWRITEBYTECODE=1


WORKDIR /app

COPY . . 


RUN pip install --no-cache--dir -r requirements.text 

COPY . / /app/


EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000", "--workers", "4"]

#CMD ['uvicorn',"main:app" ,"--host","0.0.0.0","--port","8000"]