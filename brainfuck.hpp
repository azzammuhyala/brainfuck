#ifndef BFINTERPRETER_HPP
#define BFINTERPRETER_HPP

#include <string>
#include <vector>
#include <functional>
#include <optional>
#include <map>
#include <cstdint>

using namespace std;

struct BFToken {
    size_t position;
    char character;
};

struct StepResult {
    size_t index;
    size_t point;
    size_t position;
    char character;
};

class BFInterpreter {
    private:
    vector<BFToken> tokens;
    map<size_t, size_t> bracketMap;

    public:
    bool running;
    string source;
    optional<size_t> cells;
    function<uint8_t()> input;
    function<void(uint8_t)> output;

    vector<size_t> memory;
    signed long long index;
    size_t point;

    BFInterpreter(
        string source,
        optional<size_t> cells = nullopt,
        optional<function<uint8_t()>> input = nullopt,
        optional<function<void(uint8_t)>> output = nullopt
    );
    void start();
    optional<StepResult> step();
    void stop(bool cleanUp=true);
};

void BFExec(
    string source,
    optional<size_t> cells = nullopt,
    optional<function<uint8_t()>> input = nullopt,
    optional<function<void(uint8_t)>> output = nullopt
);

#endif