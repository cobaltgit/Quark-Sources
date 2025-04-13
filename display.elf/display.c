#include <SDL/SDL.h>
#include <SDL/SDL_ttf.h>
#include <SDL/SDL_image.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 240
#define FONT_SIZE 22
#define MAX_CHARS_PER_LINE 30
#define USAGE "Usage: %s [-b background_image] [-d duration] [-f font_path] \"text\"\n"

char* wrapText(const char* text, int max_width) {
    if (!text || max_width <= 0) {
        return NULL;
    }

    size_t text_length = strlen(text);
    char* wrapped = (char*)malloc(text_length + (text_length / max_width) + 1);
    if (!wrapped) {
        return NULL;
    }

    size_t wrapped_index = 0;
    size_t line_start = 0;

    while (line_start < text_length) {
        size_t line_end = line_start + max_width;
        if (line_end >= text_length) {
            line_end = text_length;
        } else {
            while (line_end > line_start && text[line_end] != ' ') {
                line_end--;
            }
            if (line_end == line_start) {
                line_end = line_start + max_width;
            }
        }

        size_t line_length = line_end - line_start;
        memcpy(wrapped + wrapped_index, text + line_start, line_length);
        wrapped_index += line_length;

        if (line_end < text_length) {
            wrapped[wrapped_index++] = '\n';
        }

        line_start = line_end + 1;
    }

    wrapped[wrapped_index] = '\0';
    return wrapped;
}

void renderText(SDL_Surface* screen, TTF_Font* font, const char* text, SDL_Color color) {
    char* text_copy = strdup(text);
    char* line = strtok(text_copy, "\n");

    int line_height = TTF_FontHeight(font);
    int line_count = 0;

    while (line != NULL) {
        line_count++;
        line = strtok(NULL, "\n");
    }

    int total_height = line_count * line_height;
    int y_offset = (SCREEN_HEIGHT - total_height) / 2;

    free(text_copy);
    text_copy = strdup(text);
    line = strtok(text_copy, "\n");

    while (line != NULL) {
        SDL_Surface* text_surface = TTF_RenderText_Solid(font, line, color);
        if (text_surface) {
            int x = (SCREEN_WIDTH - text_surface->w) / 2;
            SDL_BlitSurface(text_surface, NULL, screen, &(SDL_Rect){x, y_offset, 0, 0});
            SDL_FreeSurface(text_surface);
            y_offset += line_height;
        }
        line = strtok(NULL, "\n");
    }

    free(text_copy);
}

int main(int argc, char* argv[]) {
    if (argc == 1) {
        fprintf(stderr, USAGE, argv[0]);
        return EXIT_FAILURE;
    }

    int duration = 0;
    char* font_path = "/mnt/SDCARD/System/res/TwCenMT.ttf";
    const char* background_image_path = NULL;
    int opt;

    while ((opt = getopt(argc, argv, "b:d:f:")) != -1) {
        switch (opt) {
            case 'b':
                background_image_path = optarg;
                break; 
            case 'd':
                duration = atoi(optarg);
                break;
            case 'f':
                font_path = optarg;
                break;
            default:
                fprintf(stderr, USAGE, argv[0]);
                return EXIT_FAILURE;
        }
    }

    if (optind >= argc) {
        fprintf(stderr, "%s: must provide text to display\n", argv[0]);
        fprintf(stderr, USAGE, argv[0]);
        return EXIT_FAILURE;
    }

    const char* text = argv[optind];

    putenv("SDL_VIDEO_FBCON_ROTATION=CCW");
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        fprintf(stderr, "SDL could not initialize: %s\n", SDL_GetError());
        return EXIT_FAILURE;
    }
    SDL_ShowCursor(0);

    if (TTF_Init() == -1) {
        fprintf(stderr, "TTF could not initialize: %s\n", TTF_GetError());
        SDL_Quit();
        return EXIT_FAILURE;
    }

    if (IMG_Init(IMG_INIT_PNG | IMG_INIT_JPG) == 0) {
        fprintf(stderr, "IMG could not initialize: %s\n", IMG_GetError());
        TTF_Quit();
        SDL_Quit();
        return EXIT_FAILURE;
    }

    SDL_Surface* screen = SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, 16, SDL_SWSURFACE);
    TTF_Font* font = TTF_OpenFont(font_path, FONT_SIZE);
    if (font == NULL) {
        fprintf(stderr, "Could not open font: %s\n", TTF_GetError());
        IMG_Quit();
        TTF_Quit();
        SDL_Quit();
        return EXIT_FAILURE;
    }

    SDL_Color textColor = {255, 255, 255};

    SDL_Surface* background = NULL;
    if (background_image_path) {
        background = IMG_Load(background_image_path);
        if (!background) {
            fprintf(stderr, "Failed to load background image: %s\n", IMG_GetError());
            IMG_Quit();
            TTF_Quit();
            SDL_Quit();
            return EXIT_FAILURE;
        }
    }

    if (background) {
        SDL_BlitSurface(background, NULL, screen, NULL);
        SDL_FreeSurface(background);
    } else {
        SDL_FillRect(screen, NULL, SDL_MapRGB(screen->format, 0, 0, 0));
    }

    char* wrappedText = wrapText(text, MAX_CHARS_PER_LINE);
    renderText(screen, font, wrappedText, textColor);
    SDL_Flip(screen);

    if (duration > 0) {
        SDL_Delay(duration);
    } else {
        SDL_Event event;
        int running = 1;
        while (running) {
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT) running = 0;
            }
            SDL_Delay(100);
        }
    }

    TTF_CloseFont(font);
    IMG_Quit();
    TTF_Quit();
    SDL_Quit();
    return EXIT_SUCCESS;
}