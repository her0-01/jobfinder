FROM python:3.9-slim

# Installer Chrome et dépendances
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements
COPY job_scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

WORKDIR /app/job_scraper

# Exposer le port
EXPOSE 5001

# Lancer l'app
CMD ["python", "web_app.py"]
