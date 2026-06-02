# =========================
# Stage 1: Builder
# =========================
FROM python:3.12-slim AS builder

WORKDIR /app

# Dependencias necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos necesarios para instalar el proyecto
COPY pyproject.toml .
COPY README.md .

# Copiar código fuente necesario para la instalación
COPY app ./app
COPY config.py .
COPY main.py .

# Crear entorno virtual e instalar dependencias
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir .

# =========================
# Stage 2: Runtime
# =========================
FROM python:3.12-slim

WORKDIR /app

# Dependencias necesarias en ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar entorno virtual ya preparado
COPY --from=builder /opt/venv /opt/venv

# Copiar aplicación completa
COPY . .

# Variables de entorno
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Puerto del Summary Service
EXPOSE 8002

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]