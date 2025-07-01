FROM python:3.9-slim

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    aria2 \
    qbittorrent-nox \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Setup qBittorrent
RUN mkdir -p /root/.local/share/qBittorrent && \
    chmod -R 777 /root/.local

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pymongo

# Copy application files
COPY . .
COPY .netrc /root/.netrc
RUN chmod 600 /root/.netrc
RUN chmod +x aria.sh

CMD ["bash", "start.sh"]
