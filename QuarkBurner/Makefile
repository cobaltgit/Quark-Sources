DOCKER_IMAGE = quark-burner-build
DOCKER_CT = quark-builder-ct

all: build

build:
	docker build -t $(DOCKER_IMAGE) .
	docker create --name $(DOCKER_CT) $(DOCKER_IMAGE) /bin/sh
	docker cp $(DOCKER_CT):/QuarkBurner.bin .
	docker rm --force $(DOCKER_CT)

clean:
	rm -rf QuarkBurner.bin
	docker rm --force $(DOCKER_CT)
	docker rmi $(DOCKER_IMAGE)