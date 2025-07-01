FROM python:3.9-slim

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    aria2 \
    qbittorrent-nox \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers de l'application
COPY extract /usr/local/bin
COPY pextract /usr/local/bin
RUN chmod +x /usr/local/bin/extract && chmod +x /usr/local/bin/pextract
COPY . .
COPY .netrc /root/.netrc
RUN chmod 600 /usr/src/app/.netrc
RUN chmod +x aria.sh

CMD ["bash","start.sh"]