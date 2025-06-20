TARGET := QuarkBurner
NUITKAFLAGS := --onefile --standalone --python-flag=nosite,-O \
	--plugin-enable=tk-inter,anti-bloat,implicit-imports,upx --assume-yes-for-downloads \
	--lto=yes --remove-output --show-progress --show-modules
BUILD_ENV = .build_env

all: build

env:
	python -m venv $(BUILD_ENV)
	$(BUILD_ENV)/bin/pip install -U nuitka

build: env
	$(BUILD_ENV)/bin/python -m nuitka $(NUITKAFLAGS) --output-filename=$(TARGET) $(TARGET).py

clean:
	rm -rf $(TARGET)