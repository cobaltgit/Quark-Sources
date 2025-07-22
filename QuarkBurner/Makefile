DOCKER_IMAGE = quark-burner-build

all: build

env:
	docker build -t $(DOCKER_IMAGE) .

build: env
	docker run --rm -v $(shell pwd):/app -v $(shell pwd)/dist:/app/dist $(DOCKER_IMAGE)

clean:
	rm -rf QuarkBurner.bin