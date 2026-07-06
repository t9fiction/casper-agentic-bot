FROM rust:bookworm AS builder

RUN rustup default nightly && \
    cargo install casper-client@5.0.1

FROM python:3.13-slim-bookworm

COPY --from=builder /usr/local/cargo/bin/casper-client /usr/local/bin/casper-client

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY portfolio_cache.json contracts_registry.json ./
COPY smart-contract/wasm/ smart-contract/wasm/

RUN mkdir -p /app/conversations

EXPOSE 7860

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
