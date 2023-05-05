FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    git \
    libgtk2.0-dev \
    pkg-config \
    wget \
    dbus \
    libgl1-mesa-glx\
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install numpy && \
    pip install -r requirements.txt && \
    pip install dlib

COPY . .

CMD ["streamlit", "run", "--server.port", "8080", "--server.headless", "true", "--server.enableCORS", "false", "attendance.py"]
