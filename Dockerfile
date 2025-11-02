FROM python:3.11-slim

# Đặt thư mục làm việc
WORKDIR /app

# Disable telemetry/noise in runtime
ENV CHROMA_TELEMETRY_ENABLED=false \
    ANONYMIZED_TELEMETRY=false \
    CHROMA_SERVER_NO_ANALYTICS=1 \
    LANGCHAIN_TRACING_V2=false \
    LANGCHAIN_ENDPOINT="" \
    LANGCHAIN_TELEMETRY=false \
    LANGSMITH_API_KEY=""

# Cài đặt các gói hệ thống cần thiết (nếu có gói biên dịch như chromadb, pydantic,...)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements
COPY requirements.txt .

# Cài thư viện Python
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source vào container
COPY . .

# Expose cổng cho FastAPI
EXPOSE 8000

# Chạy server (có reload để dev tiện)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
