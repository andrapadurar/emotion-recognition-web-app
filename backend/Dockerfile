FROM python:3.11-slim

#setăm directorul de lucru
WORKDIR /app

#dependențele necesare pentru OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

#instalăm bibliotecile Python
RUN pip install --no-cache-dir -r requirements.txt

#copiem codul aplicației
COPY . .

#expunem portul utilizat de FastAPI
EXPOSE 8000

#pornim serverul FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]