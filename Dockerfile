FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copiar el resto del código
COPY . .
CMD ["python", "app.py"]