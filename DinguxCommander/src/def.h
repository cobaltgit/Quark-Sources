#ifndef _DEF_H_
#define _DEF_H_

//~ #define INHIBIT(X) X
#define INHIBIT(X) /* X */

#ifndef FONTS
#define FONTS {"/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",10},{"FreeSans.ttf",10},{"DroidSansFallback.ttf",9}
#endif

// Font stack to use on screens with low DPI.
#ifndef LOW_DPI_FONTS
#define LOW_DPI_FONTS {"Fiery_Turk.ttf",8},{"/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",10},{"FreeSans.ttf",10},{"DroidSansFallback.ttf",9}
#endif

// Panel
#define HEADER_H 17
#define HEADER_H_PHYS static_cast<int>(HEADER_H * screen.ppu_y)
#define HEADER_PADDING_TOP 3
#define HEADER_PADDING_TOP_PHYS static_cast<int>(HEADER_PADDING_TOP * screen.ppu_y)

#define FOOTER_H 13
#define FOOTER_H_PHYS static_cast<int>(FOOTER_H * screen.ppu_y)
#define FOOTER_PADDING_TOP 1
#define FOOTER_PADDING_TOP_PHYS static_cast<int>(FOOTER_PADDING_TOP * screen.ppu_y)

#define Y_LIST HEADER_H
#define Y_LIST_PHYS static_cast<int>(Y_LIST * screen.ppu_y)

#define LINE_HEIGHT 15
#define LINE_HEIGHT_PHYS static_cast<int>(LINE_HEIGHT * screen.ppu_y)
#define NB_VISIBLE_LINES ((screen.actual_h - FOOTER_H_PHYS - HEADER_H_PHYS - 1) / LINE_HEIGHT_PHYS + 1)
#define NB_FULLY_VISIBLE_LINES ((screen.actual_h - FOOTER_H_PHYS - HEADER_H_PHYS) / LINE_HEIGHT_PHYS)

// Dialogs
#define DIALOG_BORDER 2
#define DIALOG_PADDING 8
// Colors
#define COLOR_TITLE_BG 0, 0, 0
#define COLOR_KEY 64, 255, 64
#define COLOR_TEXT_NORMAL 255, 64, 64
#define COLOR_TEXT_TITLE 235, 235, 235
#define COLOR_TEXT_DIR 64, 64, 255
#define COLOR_TEXT_SELECTED 255, 128, 128
#define COLOR_CURSOR_1 176, 176, 176
#define COLOR_CURSOR_2 117, 117, 117
#define COLOR_BG_1 20, 20, 20
#define COLOR_BG_2 40, 40, 40
#define COLOR_BORDER 147, 147, 147
#define COLOR_BORDER_ERROR 128, 0, 0

#endif // _DEF_H_
