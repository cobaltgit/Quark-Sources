TARGET = display
PRODUCT = $(TARGET).elf

CROSS_COMPILE ?= arm-linux-
CC = $(CROSS_COMPILE)gcc

CPUFLAGS = -mcpu=cortex-a7 -mtune=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
CFLAGS = -Os -lSDL -lSDL_ttf -lSDL_image -lrt -ldl -Wl,--gc-sections -s $(CPUFLAGS)

all:
	$(CC) $(TARGET).c -o $(PRODUCT) $(CFLAGS)
clean:
	rm -f $(PRODUCT)