FROM ubuntu:24.04

# Install dependencies including ICU for .NET
RUN apt-get update && apt-get install -y \
    git \
    wget \
    httperf \
    curl \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

# Install .NET SDK 9.0 (required by global.json - not 8.0!)
RUN wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh && \
    chmod +x dotnet-install.sh && \
    ./dotnet-install.sh --channel 9.0 --install-dir /usr/share/dotnet && \
    ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet && \
    rm dotnet-install.sh

# Verify .NET installation
RUN dotnet --version

# Clone Suave at broken commit (v3.1.0-beta6)
WORKDIR /tmp
RUN git clone https://github.com/SuaveIO/suave.git && \
    cd suave && \
    git checkout 8060f05409e72def1ef471a97b76a24ea7a54be0

# Move to /app and remove .git to prevent agents from browsing history
RUN mv suave /app && \
    rm -rf /app/.git

WORKDIR /app

# Restore dotnet tools and paket dependencies
RUN dotnet tool restore && \
    dotnet paket restore

# Build the project
RUN dotnet build Suave.sln

CMD ["bash"]