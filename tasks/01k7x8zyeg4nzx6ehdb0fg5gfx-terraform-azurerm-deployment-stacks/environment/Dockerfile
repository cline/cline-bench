FROM golang:1.24-bookworm

# Install system dependencies (tmux and asciinema required by Terminal-Bench)
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    tmux \
    asciinema \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management (Terminal-Bench requirement)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure Go is in PATH for non-interactive shells (agents need this)
ENV PATH="/usr/local/go/bin:/root/.local/bin:${PATH}"

# Create symlinks for go/gofmt in /usr/local/bin (always in PATH for all shell types)
RUN ln -s /usr/local/go/bin/go /usr/local/bin/go && \
    ln -s /usr/local/go/bin/gofmt /usr/local/bin/gofmt

# Set working directory
WORKDIR /app

# Clone repository at broken commit (Oct 17, 2025 - before deployment stacks)
RUN git clone https://github.com/hashicorp/terraform-provider-azurerm.git . && \
    git checkout a6f0f4e514d3f1ea536b89dbce0e98e436e9a283

# Download Go module dependencies
RUN GO111MODULE=on go mod download

# Remove .git to prevent agents from browsing commit history for the fix
RUN rm -rf .git

CMD ["sleep", "infinity"]
