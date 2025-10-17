#ifndef DOC_TOKEN_H_
#define DOC_TOKEN_H_

#include "./doc_addr.h"

#include <experimental/filesystem>
#include <string>

enum class TokenType
{
    Text,
    Header,
    Image,
    ListItem,
};

struct DocToken
{
    TokenType type;
    DocAddr address;

    DocToken(TokenType type, DocAddr address);
    virtual bool operator==(const DocToken &other) const;
    virtual std::string to_string() const = 0;

protected:
    std::string common_to_string(std::string data) const;
};

struct TextDocToken : public DocToken
{
    std::string text;

    TextDocToken(DocAddr address, const std::string &text);
    bool operator==(const DocToken &other) const override;
    std::string to_string() const override;
};

struct HeaderDocToken : public DocToken
{
    std::string text;

    HeaderDocToken(DocAddr address, const std::string &text);
    bool operator==(const DocToken &other) const override;
    std::string to_string() const override;
};

struct ImageDocToken : public DocToken
{
    std::experimental::filesystem::path path;

    ImageDocToken(DocAddr address, const std::experimental::filesystem::path &path);
    bool operator==(const DocToken &other) const override;
    std::string to_string() const override;
};

struct ListItemDocToken : public DocToken
{
    std::string text;
    int nest_level;

    ListItemDocToken(DocAddr address, const std::string &text, int nest_level);
    bool operator==(const DocToken &other) const override;
    std::string to_string() const override;
};

std::string to_string(TokenType type);

#endif
