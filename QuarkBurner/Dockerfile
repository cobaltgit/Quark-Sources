FROM python:slim AS build

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    pkg-config \
    tcl-dev \
    tk-dev \
    python3-tk \
    libc6-dev \
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

RUN pip install --no-cache-dir nuitka pip-system-certs certifi

WORKDIR /app

COPY . .

ENV CFLAGS="-Os -march=x86-64 -flto=auto -ffunction-sections -fdata-sections -Wl,--gc-sections -Wl,--strip-all" \
    CXXFLAGS="-Os -march=x86-64 -flto=auto -ffunction-sections -fdata-sections -Wl,--gc-sections -Wl,--strip-all" \
    LDFLAGS="-flto=auto -Wl,--gc-sections -Wl,--strip-all"

RUN python -m nuitka \
     --onefile \
     --python-flag=nosite,-OO \
     --plugin-enable=tk-inter,anti-bloat,implicit-imports,upx \
     --assume-yes-for-downloads \
     --include-package=certifi \
     --lto=yes \
     --remove-output \
     --show-progress \
     --show-modules \
     QuarkBurner.py

FROM scratch AS output

COPY --from=build /app/QuarkBurner.bin /
