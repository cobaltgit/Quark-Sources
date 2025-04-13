#include <SDL/SDL.h>
#include <SDL/SDL_mixer.h>
#include <SDL/SDL_ttf.h>
#include <stdio.h>
#include <stdlib.h>
#include <libgen.h>
#include <unistd.h>

#define WINDOW_WIDTH 320
#define WINDOW_HEIGHT 240
#define FONT "/mnt/SDCARD/System/res/TwCenMT.ttf"
#define FONT_SIZE 24

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
    int y_offset = (WINDOW_HEIGHT - total_height) / 2;

    free(text_copy);
    text_copy = strdup(text);
    line = strtok(text_copy, "\n");

    while (line != NULL) {
        SDL_Surface* text_surface = TTF_RenderText_Solid(font, line, color);
        if (text_surface) {
            int x = (WINDOW_WIDTH - text_surface->w) / 2;
            SDL_BlitSurface(text_surface, NULL, screen, &(SDL_Rect){x, y_offset, 0, 0});
            SDL_FreeSurface(text_surface);
            y_offset += line_height;
        }
        line = strtok(NULL, "\n");
    }

    free(text_copy);
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <mp3-file>\n", argv[0]);
        return 1;
    }
    
    putenv("SDL_VIDEO_FBCON_ROTATION=CCW");
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER) < 0) {
        fprintf(stderr, "SDL could not initialize! SDL Error: %s\n", SDL_GetError());
        return 1;
    }
    SDL_ShowCursor(0);

    if (TTF_Init() == -1) {
        fprintf(stderr, "TTF could not initialize: %s\n", TTF_GetError());
        SDL_Quit();
        return 0;
    }

    SDL_Surface* screen = SDL_SetVideoMode(WINDOW_WIDTH, WINDOW_HEIGHT, 16, SDL_SWSURFACE);
    TTF_Font* font = TTF_OpenFont(FONT, FONT_SIZE);
    if (font == NULL) {
        fprintf(stderr, "Could not open font: %s\n", TTF_GetError());
        TTF_Quit();
        SDL_Quit();
        return 1;
    }

    if (Mix_OpenAudio(44100, AUDIO_S16, 2, 2048) < 0) {
        fprintf(stderr, "SDL_mixer could not initialize! SDL_mixer Error: %s\n", Mix_GetError());
        TTF_CloseFont(font);
        TTF_Quit();
        SDL_Quit();
        return 1;
    }
    Mix_AllocateChannels(16);
    
    Mix_Music* music = Mix_LoadMUS(argv[1]);
    if (music == NULL) {
        fprintf(stderr, "Failed to load MP3 file! SDL_mixer Error: %s\n", Mix_GetError());
        Mix_CloseAudio();
        TTF_CloseFont(font);
        TTF_Quit();
        SDL_Quit();
        return 1;
    }
    
    if (Mix_PlayMusic(music, 1) < 0) {
        fprintf(stderr, "Failed to play MP3 file! SDL_mixer Error: %s\n", Mix_GetError());
        Mix_FreeMusic(music);
        Mix_CloseAudio();
        TTF_CloseFont(font);
        TTF_Quit();
        SDL_Quit();
        return 1;
    }
    
    printf("Playing: %s\n", argv[1]);

    char text[256];
    snprintf(text, sizeof(text), "Now playing: %s", basename(argv[1]));

    char* wrappedText = wrapText(text, 30);
    SDL_Color textColor = {255, 255, 255};
    
    renderText(screen, font, wrappedText, textColor);
    SDL_Flip(screen);
    
    int done = 0;
    int paused = 0;
    double estimatedPos = 0.0;
    Uint32 lastTime = SDL_GetTicks();
    SDL_Event event;
    
    while (!done) {
        
        if (!paused && Mix_PlayingMusic()) {
            Uint32 currentTime = SDL_GetTicks();
            estimatedPos += (currentTime - lastTime) / 1000.0;
            lastTime = currentTime;
        } else {
            lastTime = SDL_GetTicks();
        }

        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_KEYDOWN) {
                switch (event.key.keysym.sym) {
                    case SDLK_ESCAPE:
                        done = 1;
                        break;
                    case SDLK_SPACE:
                        if (!paused) {
                            Mix_PauseMusic();
                            paused = 1;
                        } else {
                            Mix_ResumeMusic();
                            paused = 0;
                        }
                        break;
                    case SDLK_LEFT:
                        estimatedPos -= 10.0;
                        if (estimatedPos < 0.0) estimatedPos = 0.0;
                        Mix_SetMusicPosition(estimatedPos);
                        break;
                    case SDLK_RIGHT:
                        estimatedPos += 10.0;
                        Mix_SetMusicPosition(estimatedPos);
                        break;
                    case SDLK_UP:
                        estimatedPos += 20.0;
                        Mix_SetMusicPosition(estimatedPos);
                        break;
                    case SDLK_DOWN:
                        estimatedPos -= 20.0;
                        if (estimatedPos < 0.0) estimatedPos = 0.0;
                        Mix_SetMusicPosition(estimatedPos);
                        break;
                }
            }
        }
        
        if (!Mix_PlayingMusic()) {
            printf("Playback finished.\n");
            done = 1;
        }
        
        SDL_Delay(50);
    }
    
    printf("Cleaning up...\n");
    Mix_HaltMusic();
    Mix_FreeMusic(music);
    Mix_CloseAudio();
    TTF_CloseFont(font);
    TTF_Quit();
    SDL_Quit();
    
    return 0;
}