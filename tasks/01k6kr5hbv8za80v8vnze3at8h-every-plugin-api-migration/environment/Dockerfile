FROM ubuntu:24.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    unzip \
    tmux \
    asciinema \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Bun (used by the project)
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun && \
    ln -s /root/.bun/bin/bunx /usr/local/bin/bunx

# Install uv (Python package manager for Terminal-Bench tests)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.cargo/bin/uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Clone repository at broken commit
RUN git clone https://github.com/near-everything/every-plugin.git . && \
    git checkout 85ca674246b3987e9d4b7c7ca454a1885291cbcc

# Install dependencies (use bun as the project uses it)
RUN bun install

# Remove .git to prevent agents from browsing history for the fix
RUN rm -rf .git

# Keep container alive for Harbor/Daytona/E2B
CMD ["sleep", "infinity"]
