TARGET = mp3player
PRODUCT = $(TARGET).elf

CROSS_COMPILE ?= arm-linux-
CC = $(CROSS_COMPILE)gcc

CPUFLAGS = -march=armv7ve+simd -mtune=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
CFLAGS = -O3 -lSDL -lSDL_ttf -lSDL_mixer -lrt -ldl -Wl,--gc-sections -s $(CPUFLAGS)

all:
	$(CC) $(TARGET).c -o $(PRODUCT) $(CFLAGS)
clean:
	rm -f $(PRODUCT)