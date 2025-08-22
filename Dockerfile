# ── Dockerfile ──────────────────────────────────────────────
FROM python:3.11-slim

# 1. System packages (if you need ffmpeg or others, add here)
RUN apt-get update && apt-get install -y \
        git \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy project and install deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of the source
COPY . .

# 4. Default command (overridden by compose)
CMD ["bash"]
