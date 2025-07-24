#include <iostream>
#include <vector>
#include <variant>
#include <optional>
#include <functional>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <map>

using namespace std;

uint8_t _default_input() {
    while (true) {
        char character;
        cin.get(character);

        if (cin) {
            return static_cast<uint8_t>(static_cast<unsigned char>(character));
        }
    }
}

void _default_output(uint8_t byte) {
    cout.put(static_cast<char>(byte));
    cout.flush();
}

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
    ) {

        this->running = false;

        this->source = source;
        this->cells = cells;
        this->input = input.has_value() ? input.value() : _default_input;
        this->output = output.has_value() ? output.value() : _default_output;

        this->tokens = {};
        this->bracketMap = {};

        vector<size_t> stack = {};
        bool comment = false;
        size_t tokenIndex = 0;

        for (
            size_t position = 0;
            position < source.size();
            position++
        ) {
            char character = source[position];

            if (!comment && character == '#') {
                comment = true;
            }
            else if (comment && character == '\n') {
                comment = false;
            }

            if (!comment && (
                character == '<' ||
                character == '>' ||
                character == '+' ||
                character == '-' ||
                character == '.' ||
                character == ',' ||
                character == '[' ||
                character == ']'
            )) {

                if (character == '[') {
                    stack.push_back(tokenIndex);
                }

                else if (character == ']') {
                    if (stack.empty()) {
                        throw runtime_error("unbalanced brackets");
                    }

                    size_t startIndex = stack.back();

                    this->bracketMap[startIndex] = tokenIndex;
                    this->bracketMap[tokenIndex] = startIndex;

                    stack.pop_back();
                }

                BFToken token = {position, character};

                this->tokens.push_back(token);
                tokenIndex++;
            }
        }

        if (!stack.empty()) {
            throw runtime_error("unbalanced brackets");
        }
    }

    void start() {
        if (this->running) {
            return;
        }

        this->running = true;
        this->memory = this->cells.has_value() ?
                        vector<size_t>(this->cells.value()) :
                        vector<size_t>(1, 0);
        this->index = -1;
        this->point = 0;
    }

    optional<StepResult> step() {
        if (!this->running) {
            return nullopt;
        }

        this->index++;

        if (this->index >= this->tokens.size()) {
            this->running = false;
            return nullopt;
        }

        BFToken token = this->tokens[this->index];
        uint8_t dataPointer = (this->point < this->memory.size()) ? this->memory[this->point] : 0;

        if (token.character == '>') {
            this->point++;
            if (!this->cells.has_value()) {
                if (this->point == this->memory.size()) {
                    this->memory.push_back(0);
                }
            }
            else if (this->point >= this->cells.value()) {
                throw runtime_error("pointer out of bounds");
            }
        }

        else if (token.character == '<') {
            if (this->point == 0) {
                throw runtime_error("pointer out of bounds");
            }
            this->point--;
        }

        else if (token.character == '+') {
            this->memory[this->point] = (this->memory[this->point] + 1) % 256;
        }

        else if (token.character == '-') {
            this->memory[this->point] = (this->memory[this->point] - 1) % 256;
        }

        else if (token.character == ',') {
            this->memory[this->point] = this->input();
        }

        else if (token.character == '.') {
            this->output(this->memory[this->point]);
        }

        else if (token.character == '[' && this->memory[this->point] == 0) {
            this->index = this->bracketMap[this->index];
        }

        else if (token.character == ']' && this->memory[this->point] != 0) {
            this->index = this->bracketMap[this->index];
        }

        StepResult result = {
            static_cast<size_t>(this->index),
            this->point,
            token.position,
            token.character
        };

        return result;
    }

    void stop(bool cleanUp=true) {
        if (!this->running) {
            return;
        }

        this->running = false;

        if (cleanUp) {
            this->memory.clear();
            this->index = -1;
            this->point = 0;
        }
    }
};

void BFExec(
    string source,
    optional<size_t> cells = nullopt,
    optional<function<uint8_t()>> input = nullopt,
    optional<function<void(uint8_t)>> output = nullopt
) {
    BFInterpreter interpreter(source, cells, input, output);
    interpreter.start();
    while (interpreter.running) {interpreter.step();}
    interpreter.stop();
}