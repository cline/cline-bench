FROM ubuntu:24.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Terminal-Bench test runner
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install Miniforge (conda-compatible, conda-forge by default, no TOS issues)
# Use architecture-agnostic uname to download correct version
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        MINIFORGE_ARCH="x86_64"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        MINIFORGE_ARCH="aarch64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${MINIFORGE_ARCH}.sh -O /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p /opt/conda && \
    rm /tmp/miniforge.sh

ENV PATH="/opt/conda/bin:$PATH"

# Create aenet-torch conda environment with Python
RUN conda create -n aenet-torch python=3.11 -y && \
    conda clean -afy

# Install torch and base dependencies
# Use numpy<2.0 for compatibility with torch 2.1.0 (compiled with NumPy 1.x)
RUN conda run -n aenet-torch pip install --no-cache-dir \
    torch==2.1.0 \
    'numpy>=1.20.0,<2.0' \
    'scipy>=1.9.0,<2.0' \
    'pandas>=1.2.4' \
    'tables>=3.6.1' \
    'tqdm>=4.62.3' \
    'matplotlib>=3.3.4' \
    pytest

# Install torch-scatter and torch-cluster separately without build isolation
# (they need torch available during build)
RUN conda run -n aenet-torch pip install --no-cache-dir --no-build-isolation torch-scatter torch-cluster

# Clone repository at BROKEN commit (starting state)
RUN git clone https://github.com/atomisticnet/aenet-python.git /app && \
    cd /app && git checkout ab777f944c5727c2480ad3a85ba566693fd8fa41

# Fix scipy and numpy dependencies in pyproject.toml before installing
# - scipy>=2.0.0 doesn't exist (typo in upstream)
# - numpy needs <2.0 for torch 2.1.0 compatibility
RUN cd /app && \
    sed -i 's/scipy>=2\.0\.0/scipy>=1.9.0,<2.0/' pyproject.toml && \
    sed -i 's/"numpy",/"numpy>=1.20.0,<2.0",/' pyproject.toml

# Install aenet package in development mode in conda env
RUN cd /app && conda run -n aenet-torch pip install -e .

# Remove .git to prevent agents from browsing history
RUN cd /app && rm -rf .git

# Set conda environment activation for all shells
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate aenet-torch" >> /root/.bashrc

WORKDIR /app