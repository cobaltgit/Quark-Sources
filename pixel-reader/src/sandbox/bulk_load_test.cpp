#include "doc_api/token_addressing.h"
#include "filetypes/open_doc.h"
#include "reader/config.h"
#include "reader/ss_doc_reader_cache.h"
#include "reader/state_store.h"
#include "util/timer.h"

#include <experimental/filesystem>
#include <iostream>
#include <list>
#include <string>

namespace
{

struct Stats
{
    std::list<std::pair<std::string, uint32_t>> load_times;
};

void load_file(std::experimental::filesystem::path path, Stats &stats, DocReaderCache &cache)
{
    Timer t;

    auto reader = create_doc_reader(path);
    if (!reader || !reader->open(cache))
    {
        std::cerr << "Unable to open " << path.filename() << std::endl;
        return;
    }

    stats.load_times.emplace_back(
        path.filename(), t.elapsed_ms()
    );
}

} // namespace

void bulk_load_test(std::string dir_path)
{
    if (std::experimental::filesystem::exists(dir_path) && std::experimental::filesystem::is_directory(dir_path))
    {
        StateStore store("store");
        SSDocReaderCache cache(store);

        Stats stats;

        for (const auto& entry: std::experimental::filesystem::directory_iterator(dir_path))
        {
            load_file(entry.path(), stats, cache);
        }

        uint32_t total_load_time = 0;
        for (const auto &times: stats.load_times)
        {
            const auto &path = times.first;
            const auto load_time = times.second;
            std::cerr << path << ", " << load_time << std::endl;

            total_load_time += load_time;
        }

        std::cerr << std::endl;
        std::cerr << "Total files: " << stats.load_times.size() << std::endl;
        std::cerr << "Total time: " << total_load_time << std::endl;

        {
            Timer t;
            store.flush();
            std::cerr << "Flush time: " << t.elapsed_ms() << std::endl;
        }
    }
    else
    {
        std::cerr << "Invalid directory" << std::endl;
    }
}
