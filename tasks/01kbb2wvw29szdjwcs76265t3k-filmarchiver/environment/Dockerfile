FROM ubuntu:24.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management (Harbor standard)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Clone repository at broken commit (v1.2.0)
RUN git clone https://github.com/Wetdogtaste/Film-Archiver.git . && \
    git checkout 075453d1afe3f0b6b5f08dc82364d01469208c72

# Install Python dependencies needed for verification
# Pillow is needed to test create_dmg_background.py can run
RUN python3 -m pip install --break-system-packages Pillow

# Remove .git to prevent agents from browsing commit history
RUN rm -rf .git

# Set working directory to film_archiver_app subdirectory where the code lives
WORKDIR /app/film_archiver_app

CMD ["sleep", "infinity"]