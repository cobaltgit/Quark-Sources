#ifndef CLI_WRAP_LINES_H_
#define CLI_WRAP_LINES_H_

#include "doc_api/doc_token.h"
#include <string>
#include <vector>

struct Line
{
    std::string text;
    DocAddr address;

    Line(std::string text, DocAddr address);
};

// Text-only rendering of tokens.
std::vector<Line> cli_render_tokens(
    const std::vector<const DocToken *> &tokens,
    uint32_t max_column_width
);

#endif
