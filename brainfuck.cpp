#include <iostream>
#include <cstdint>
#include <functional>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>
#include <variant>

// #include "BRAINFUCK.hpp"

using namespace std;

#ifdef _WIN32
    #include <conio.h>
#else
    #include <termios.h>
    #include <unistd.h>
    int getch() {
        struct termios oldt, newt;
        int character;
        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);
        character = getchar();
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
        return character;
    }
#endif

uint8_t _BFDefaultInput() {
    while (true) {
        int result = getch();
        if (result >= 0 && result <= 255) {
            return static_cast<uint8_t>(result);
        }
    }
}

void _BFDefaultOutput(uint8_t byte) {
    cout.put(static_cast<char>(byte));
    cout.flush();
}

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
    ) {

        this->running = false;
        this->starting = false;

        this->source = source;
        this->cells = cells;
        this->input = input.has_value() ? input.value() : _BFDefaultInput;
        this->output = output.has_value() ? output.value() : _BFDefaultOutput;

        this->tokenIndex = 0;
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
                        throw logic_error("unbalanced brackets");
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
            throw logic_error("unbalanced brackets");
        }
    }

    void start() {
        if (this->running) {
            return;
        }

        this->tokenIndex = 0;

        this->running = true;
        this->starting = true;
        this->memory = this->cells.has_value() ? vector<uint8_t>(this->cells.value(), 0) : vector<uint8_t>(1, 0);
        this->point = 0;
    }

    optional<BFStepResult> step() {
        if (!this->running) {
            return nullopt;
        }

        if (this->starting) {
            this->starting = false;
        }
        else {
            this->tokenIndex++;
        }

        if (this->tokenIndex >= this->tokens.size()) {
            this->running = false;
            return nullopt;
        }

        BFToken token = this->tokens[this->tokenIndex];
        uint8_t dataPointer = (this->point < this->memory.size()) ? this->memory[this->point] : 0;

        if (token.character == '>') {
            this->point++;
            if (!this->cells.has_value()) {
                if (this->point == this->memory.size()) {
                    this->memory.push_back(0);
                }
            }
            else if (this->point >= this->cells.value()) {
                throw overflow_error("pointer out of bounds");
            }
        }

        else if (token.character == '<') {
            if (this->point == 0) {
                throw overflow_error("pointer out of bounds");
            }
            this->point--;
        }

        else if (token.character == '+') {
            this->memory[this->point] = (dataPointer + 1) % 256;
        }

        else if (token.character == '-') {
            this->memory[this->point] = (dataPointer - 1) % 256;
        }

        else if (token.character == ',') {
            this->memory[this->point] = this->input();
        }

        else if (token.character == '.') {
            this->output(dataPointer);
        }

        else if (token.character == '[' && dataPointer == 0) {
            this->tokenIndex = this->bracketMap[this->tokenIndex];
        }

        else if (token.character == ']' && dataPointer != 0) {
            this->tokenIndex = this->bracketMap[this->tokenIndex];
        }

        BFStepResult result = {
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
        this->starting = false;

        if (cleanUp) {
            this->memory.clear();
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

    while (interpreter.running) {
        interpreter.step();
    }

    interpreter.stop();
}