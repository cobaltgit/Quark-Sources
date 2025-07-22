FROM python:slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    pkg-config \
    tcl-dev \
    tk-dev \
    python3-tk \
    git \
    libc6-dev \
    build-essential \
    wget \
    xz-utils \
    patchelf \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

RUN wget -O /tmp/upx.tar.xz https://github.com/upx/upx/releases/download/v5.0.2/upx-5.0.2-amd64_linux.tar.xz && \
    cd /tmp && \
    tar -xf upx.tar.xz && \
    cp upx-5.0.2-amd64_linux/upx /usr/local/bin/ && \
    chmod +x /usr/local/bin/upx && \
    rm -rf /tmp/upx*

RUN pip install nuitka pip-system-certs certifi

WORKDIR /app

COPY . .

ENV CFLAGS="-O2 -march=x86-64 -mtune=generic"
ENV CXXFLAGS="-O2 -march=x86-64 -mtune=generic"

CMD ["python", "-m", "nuitka", \
     "--onefile", \
     "--python-flag=nosite,-OO", \
     "--plugin-enable=tk-inter,anti-bloat,implicit-imports,upx", \
     "--assume-yes-for-downloads", \
     "--include-package=certifi", \
     "--lto=yes", \
     "--remove-output", \
     "--show-progress", \
     "--show-modules", \
     "QuarkBurner.py"]