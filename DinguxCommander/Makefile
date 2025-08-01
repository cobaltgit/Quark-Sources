#
#	DinguxCommander Makefile for TRIMUI smart
#		based on https://github.com/od-contrib/commander
#

CROSS_COMPILE ?= arm-linux-
CXX := $(CROSS_COMPILE)g++
CXXFLAGS := -Os -marm -mcpu=cortex-a7 -mtune=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard -flto -Wl,--gc-sections -s
SDL_CONFIG := $(shell $(CXX) -print-sysroot)/usr/bin/sdl-config
CXXFLAGS += $(shell $(SDL_CONFIG) --cflags)

CXXFLAGS += -DPATH_DEFAULT=\"/mnt/SDCARD\"
CXXFLAGS += -DFILE_SYSTEM=\"/dev/mmcblk1p1\"
CXXFLAGS += -DCMDR_KEY_UP=SDLK_UP
CXXFLAGS += -DCMDR_KEY_RIGHT=SDLK_RIGHT
CXXFLAGS += -DCMDR_KEY_DOWN=SDLK_DOWN
CXXFLAGS += -DCMDR_KEY_LEFT=SDLK_LEFT
CXXFLAGS += -DCMDR_KEY_OPEN=SDLK_SPACE		# A
CXXFLAGS += -DCMDR_KEY_PARENT=SDLK_LCTRL	# B
CXXFLAGS += -DCMDR_KEY_OPERATION=SDLK_LSHIFT	# X
CXXFLAGS += -DCMDR_KEY_SYSTEM=SDLK_LALT		# Y
CXXFLAGS += -DCMDR_KEY_PAGEUP=SDLK_TAB		# L
CXXFLAGS += -DCMDR_KEY_PAGEDOWN=SDLK_BACKSPACE	# R
CXXFLAGS += -DCMDR_KEY_SELECT=SDLK_RCTRL	# SELECT
CXXFLAGS += -DCMDR_KEY_TRANSFER=SDLK_RETURN	# START
CXXFLAGS += -DCMDR_KEY_MENU=SDLK_ESCAPE		# MENU (added)
CXXFLAGS += -DOSK_KEY_SYSTEM_IS_BACKSPACE=ON
CXXFLAGS += -DFONTS='{"/usr/trimui/res/OPPOSans-B-2.ttf",10},{"/usr/trimui/res/Samsung-Sharp-Sans-Bold-2.ttf",10}'
CXXFLAGS += -DLOW_DPI_FONTS='{"Fiery_Turk.ttf",8},{"/usr/trimui/res/OPPOSans-B-2.ttf",9}'
CXXFLAGS += -DTRIMUISMART
#CXXFLAGS += -DVSYNCWAIT
LTO := -flto

RESDIR := res
CXXFLAGS += -DRESDIR="\"$(RESDIR)\""

LINKFLAGS += -s
LINKFLAGS += $(shell $(SDL_CONFIG) --libs) -lSDL_image -lSDL_ttf -flto

CMD := @
SUM := @echo

OUTDIR := ./output

EXECUTABLE := $(OUTDIR)/DinguxCommander

OBJS :=	main.o commander.o config.o dialog.o fileLister.o fileutils.o keyboard.o panel.o resourceManager.o \
	screen.o sdl_ttf_multifont.o sdlutils.o text_edit.o utf8.o text_viewer.o image_viewer.o  window.o \
	axis_direction.o SDL_rotozoom.o

DEPFILES := $(patsubst %.o,$(OUTDIR)/%.d,$(OBJS))

.PHONY: all clean

all: $(EXECUTABLE)

$(EXECUTABLE): $(addprefix $(OUTDIR)/,$(OBJS))
	$(SUM) "  LINK    $@"
	$(CMD)$(CXX) $(LINKFLAGS) $(LTO) -o $@ $^

$(OUTDIR)/%.o: src/%.cpp
	@mkdir -p $(@D)
	$(SUM) "  CXX     $@"
	$(CMD)$(CXX) $(CXXFLAGS) $(LTO) -MP -MMD -MF $(@:%.o=%.d) -c $< -o $@
	@touch $@ # Force .o file to be newer than .d file.

$(OUTDIR)/%.o: src/%.c
	@mkdir -p $(@D)
	$(SUM) "  CXX     $@"
	$(CMD)$(CXX) $(CXXFLAGS) $(LTO) -MP -MMD -MF $(@:%.o=%.d) -c $< -o $@
	@touch $@ # Force .o file to be newer than .d file.

clean:
	$(SUM) "  RM      $(OUTDIR)"
	$(CMD)rm -rf $(OUTDIR)

# Load dependency files.
-include $(DEPFILES)

# Generate dependencies that do not exist yet.
# This is only in case some .d files have been deleted;
# in normal operation this rule is never triggered.
$(DEPFILES):
