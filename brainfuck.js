export const BF_DEFAULT_CELL = 30000;

export function BFTokens(source) {
    if (typeof source !== 'string') {
        throw new Error("bf_tokens() source must be string");
    }

    let comment = false;
    let tokens = [];

    for (let position = 0; position < source.length; position++) {
        let character = source[position];

        if (!comment && character === '#') {
            comment = true;
        } else if (comment && character === '\n') {
            comment = false;
        }

        if (!comment && ['<', '>', '+', '-', '.', ',', '[', ']'].includes(character)) {
            tokens.push([position, character]);
        }
    }

    return tokens;
}

export class BFInterpreter {

    constructor (source, cell=null, input=null, output=null) {
        if (cell === null) {
            cell = BF_DEFAULT_CELL;
        }

        if (input === null) {
            input = () => {
                while (true) {
                    let result = prompt('Brainfuck Input');
                    if (typeof result === 'string') {
                        result = result.charCodeAt(0);
                        if (Number.isInteger(result) && result >= 0 && result <= 255) {
                            return result;
                        }
                    }
                }
            }
        }

        if (output === null) {
            output = (value) => {
                console.log(String.fromCharCode(value));
            }
        }

        if (!Number.isInteger(cell) || cell <= 0) {
            throw new Error("BFInterpreter() cell must be integer and greater than 0");
        }
        if (typeof input !== 'function') {
            throw new Error("BFInterpreter() input must be function");
        }
        if (typeof output !== 'function') {
            throw new Error("BFInterpreter() output must be function");
        }

        this.tokens = BFTokens(source);
        this.cell = cell;
        this.input = input;
        this.output = output;

        this.begin = false;
        this.bracketMap = {};

        let stack = [];

        for (let i = 0; i < this.tokens.length; i++) {
            let character = this.tokens[i][1];

            if (character === '[') {
                stack.push(i);
            }

            else if (character === ']') {
                if (stack.length === 0) {
                    throw new Error("unbalanced brackets");
                }

                let startIndex = stack.pop();

                this.bracketMap[startIndex] = i;
                this.bracketMap[i] = startIndex;
            }
        }

        if (stack.length !== 0) {
            throw new Error("unbalanced brackets");
        }
    }

    start() {
        if (this.begin) return;

        this.memory = new Array(this.cell);
        this.index = -1;
        this.pointer = 0;
        this.begin = true;
    }

    step() {
        if (!this.begin) return;

        this.index += 1;

        let stop = true;
        let position, character;

        while (this.index < this.tokens.length) {
            let point = this.memory[this.pointer] || 0;

            [position, character] = this.tokens[this.index];

            if (character === '>') {
                this.pointer += 1;
                if (this.pointer >= this.cell) {
                    throw new Error("pointer out of bounds");
                }
            }

            else if (character === '<') {
                this.pointer -= 1;
                if (this.pointer < 0) {
                    throw new Error("pointer out of bounds");
                }
            }

            else if (character === '+') {
                this.memory[this.pointer] = (point + 1) % 256;
            }

            else if (character === '-') {
                this.memory[this.pointer] = (point - 1) % 256;
            }

            else if (character === ',') {
                let input = this.input();

                if (!(Number.isInteger(input) && input >= 0 && input <= 255)) {
                    throw new Error("BFInterpreter() input must be returns unsigned 8-bit integer");
                }

                this.memory[this.pointer] = input;
            }

            else if (character === '.') {
                this.output(point);
            }

            else if (character === '[') {
                if (point === 0) {
                    this.index = this.bracketMap[this.index];
                }
            }

            else if (character === ']') {
                if (point !== 0) {
                    this.index = this.bracketMap[this.index];
                }
            }

            stop = false;
            break;
        }

        if (stop) {
            this.begin = false;
            return;
        }

        return [this.index, this.pointer, position, character];
    }

    stop() {
        this.begin = false;
    }
}

export function BFExec(source, cell=null, input=null, output=null) {
    let interpreter = new BFInterpreter(source, cell, input, output);
    interpreter.start();
    while (interpreter.begin) interpreter.step();
}