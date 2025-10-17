#ifndef XHTML_PARSER_H_
#define XHTML_PARSER_H_

#include "doc_api/doc_token.h"

#include <experimental/filesystem>
#include <string>
#include <unordered_map>
#include <vector>

bool parse_xhtml_tokens(const char *xml_str, std::experimental::filesystem::path file_path, uint32_t chapter_number, std::vector<std::unique_ptr<DocToken>> &tokens_out, std::unordered_map<std::string, DocAddr> &id_to_addr_out);

#endif
