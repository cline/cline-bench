FROM node:20-slim

WORKDIR /app

# Install git, python3, tmux, asciinema, and pnpm
RUN apt-get update && \
    apt-get install -y git python3 python3-pip curl tmux asciinema && \
    corepack enable && \
    corepack prepare pnpm@9.0.0 --activate && \
    rm -rf /var/lib/apt/lists/*

# Install uv for test environment management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

# Clone repository at broken commit
RUN git clone https://github.com/klogt-as/intercept.git . && \
    git checkout 2fe4969efcfda56c849553323581ba91cfd80ba3

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the project
RUN pnpm run build

# Keep a copy of broken state for meta-testing
RUN cp -r /app /app-broken

# Remove .git from main workspace (prevent agents from browsing history)
RUN rm -rf /app/.git

# Also remove from broken copy
RUN rm -rf /app-broken/.git

# Keep container running
CMD ["sleep", "infinity"]
