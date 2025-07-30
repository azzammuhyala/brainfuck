#ifndef BRAINFUCK_HPP
#define BRAINFUCK_HPP

#include <cstdint>
#include <functional>
#include <map>
#include <optional>
#include <string>
#include <vector>

using namespace std;

struct BFToken {
    size_t position;
    char character;
};

struct BFStepResult {
    size_t point;
    size_t position;
    char character;
};

class BFInterpreter {
    private:
    size_t tokenIndex;
    vector<BFToken> tokens;
    map<size_t, size_t> bracketMap;

    public:
    bool running;
    bool starting;
    string source;
    optional<size_t> cells;
    function<uint8_t()> input;
    function<void(uint8_t)> output;

    vector<uint8_t> memory;
    size_t point;

    BFInterpreter(
        string source,
        optional<size_t> cells = nullopt,
        optional<function<uint8_t()>> input = nullopt,
        optional<function<void(uint8_t)>> output = nullopt
    );
    void start();
    optional<BFStepResult> step();
    void stop(bool cleanUp=true);
};

void BFExec(
    string source,
    optional<size_t> cells = nullopt,
    optional<function<uint8_t()>> input = nullopt,
    optional<function<void(uint8_t)>> output = nullopt
);

#endif