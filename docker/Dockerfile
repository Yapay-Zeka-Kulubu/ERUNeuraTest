# ERUNeuraTest Docker Image
# LLM tabanlı otomatik Python birim test üretimi

FROM python:3.10-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kaynak kodları kopyala
COPY src/ ./src/
COPY examples/ ./examples/
COPY pyproject.toml .
COPY readme.md .

# Paketi yükle
RUN pip install -e .

# Ortam değişkenleri (runtime'da override edilebilir)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Varsayılan komut
CMD ["python", "-m", "src.main"]
