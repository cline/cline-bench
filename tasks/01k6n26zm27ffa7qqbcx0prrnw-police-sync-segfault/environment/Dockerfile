FROM ubuntu:24.04
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management (Terminal-Bench pattern)
RUN curl -LsSf https://astral.sh/uv/0.7.13/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

# Clone repository at BROKEN commit (starting state for agent)
WORKDIR /app
RUN git clone https://github.com/AndreasThinks/your-police-events.git . && \
    git checkout bdaff376422cd7fb3fc0b8d70f045c6700517617 && \
    rm -rf .git  # Remove git history so agent can't cheat by browsing commits

# Install Python dependencies using uv and pyproject.toml
RUN uv venv .venv && \
    . .venv/bin/activate && \
    uv pip install -e ".[test]"

# Set working directory for agent
WORKDIR /app
