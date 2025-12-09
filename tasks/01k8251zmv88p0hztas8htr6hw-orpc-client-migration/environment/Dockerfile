# Terminal-Bench Environment: oRPC Client Migration
# Task: Migrate 4 React components from fetch() to type-safe oRPC client
# Repository: https://github.com/jlwaugh/neargov
# Starting commit: fd3ea2506aa3e8400fb805df94ba968170603676

FROM ubuntu:24.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    tmux \
    asciinema \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install uv for Python package management (Terminal-Bench requirement)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Clone repository at broken commit (before oRPC client migration)
RUN git clone https://github.com/jlwaugh/neargov . && \
    git checkout fd3ea2506aa3e8400fb805df94ba968170603676

# Install dependencies
# Note: Using npm instead of bun as it's more standard and reliable in Docker
RUN npm install

# Remove .git to prevent agents from browsing commit history for the fix
RUN rm -rf .git

# Set up environment for Next.js
ENV NODE_ENV=development
