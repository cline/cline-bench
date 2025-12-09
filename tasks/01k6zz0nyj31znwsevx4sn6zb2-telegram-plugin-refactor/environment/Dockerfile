# Terminal-Bench Task: Telegram Plugin Refactoring
# Base: Ubuntu 24.04 with Node.js 20 and Bun

FROM ubuntu:24.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    unzip \
    tmux \
    asciinema \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun

# Install uv (Python package manager for test environment)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Clone repository at broken state
WORKDIR /app
RUN git clone https://github.com/near-everything/every-plugin.git . && \
    git checkout fa16847de7b09318eb9cf68df380aa36cae800fd && \
    rm -rf .git

# Install dependencies at broken state
RUN bun install

WORKDIR /app

# Keep container running
CMD ["sleep", "infinity"]
