FROM python:3.14-slim

WORKDIR /app

# System deps for PyMuPDF + antiword + LibreOffice for legacy formats
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    antiword \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-impress \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads outputs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
