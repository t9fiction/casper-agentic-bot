FROM rust:bookworm AS builder

RUN rustup default nightly && \
    cargo install casper-client@5.0.1

FROM python:3.13-slim-bookworm

RUN useradd -m -u 1000 user

COPY --from=builder /usr/local/cargo/bin/casper-client /usr/local/bin/casper-client

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user src/ src/
COPY --chown=user portfolio_cache.json contracts_registry.json ./
RUN mkdir -p /app/smart-contract/wasm && \
    python3 -c "
import urllib.request
base = 'https://github.com/t9fiction/casper-agentic-bot/releases/download/wasm-v1'
for f in ['TokenFactory.wasm', 'NftMarketplace.wasm', 'CollectionFactory.wasm']:
    urllib.request.urlretrieve(f'{base}/{f}', f'/app/smart-contract/wasm/{f}')
" && \
    chown user:user /app/smart-contract/wasm/*

RUN mkdir -p /app/conversations && chown user:user /app/conversations
RUN chown user:user /app

USER user
ENV PATH="/home/user/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
