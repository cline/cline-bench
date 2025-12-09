FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (Ubuntu 22.04 has Python 3.10)
# Note: git is needed for both environment setup AND for tests to fetch test files
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3.10 \
    python3.10-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --set python3 /usr/bin/python3.10

# Install Poetry and uv
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Install uv for test isolation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.cargo/bin/uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Clone repository at broken commit
RUN git clone https://github.com/dotimplement/HealthChain.git . && \
    git fetch origin eaac9b9f07f784e99dd7c4774e235c633a5f665f && \
    git checkout eaac9b9f07f784e99dd7c4774e235c633a5f665f

# Install dependencies with Poetry
# Configure poetry to create virtualenv in project
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi

# Remove .git to prevent agents from browsing history
RUN rm -rf .git

# Set Poetry environment variables
ENV PATH="/app/.venv/bin:$PATH"

CMD ["sleep", "infinity"]