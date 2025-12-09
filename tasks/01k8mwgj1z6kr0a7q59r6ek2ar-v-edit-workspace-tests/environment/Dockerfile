FROM ubuntu:24.04
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    cmake \
    build-essential \
    libncurses-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv for isolated test environments (Harbor pattern)
RUN curl -LsSf https://astral.sh/uv/0.7.13/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

# Clone repository at BROKEN commit (starting state for agent)
WORKDIR /app
RUN git clone https://github.com/sergev/v-edit.git . && \
    git checkout 793906138085d2b82ecc7deae4f21ce071c2971f && \
    rm -rf .git  # Remove git history so agent can't cheat by browsing commits

# Create build directory but don't build yet - broken state has warnings
# Agent will need to build after fixing the code
RUN mkdir build

# Set working directory for agent
WORKDIR /app