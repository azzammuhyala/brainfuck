export const BF_DEFAULT_CELL = 30000;

export function bf_tokens(source) {
    if (typeof source !== 'string') {
        throw new Error("bf_tokens() source must be string");
    }

    let comment = false;
    let tokens = [];

    for (let index = 0; index < source.length; index++) {
        let char = source[index];

        if (!comment && char === '#') {
            comment = true;
        } else if (comment && char === '\n') {
            comment = false;
        }

        if (!comment && ['<', '>', '+', '-', '.', ',', '[', ']'].includes(char)) {
            tokens.push([index, char]);
        }
    }

    return tokens
}

export class BFInterpreter {

    constructor (source, cell=null, input=null, output=null) {
        if (cell === null) {
            cell = BF_DEFAULT_CELL;
        }

        if (input === null) {
            input = () => {
                var inp = prompt('')
                if (typeof inp === 'string') {
                    return inp.charCodeAt(0);
                }
                return 0
            }
        }

        if (output === null) {
            output = (value) => {
                console.log(String.fromCharCode(value))
            }
        }

        if (!Number.isInteger(cell) || cell <= 0) {
            throw new Error("BFInterpreter() cell must be integer and greather than 0");
        }
        if (typeof input !== 'function') {
            throw new Error("BFInterpreter() input must be function");
        }
        if (typeof output !== 'function') {
            throw new Error("BFInterpreter() output must be function");
        }

        this.tokens = bf_tokens(source);
        this.cell = cell;
        this.input = input;
        this.output = output;

        this.begin = false;
        this.bracket_map = {};

        let stack = [];

        for (let i = 0; i < this.tokens.length; i++) {
            let char = this.tokens[i][1];

            if (char === '[') {
                stack.push(i);
            }

            else if (char === ']') {
                if (stack.length === 0) {
                    throw new Error("unbalanced brackets");
                }

                let start_index = stack.pop();

                this.bracket_map[start_index] = i;
                this.bracket_map[i] = start_index;
            }
        }

        if (stack.length !== 0) {
            throw new Error("unbalanced brackets");
        }
    }

    start() {
        if (!this.begin) {
            this.array = new Array(this.cell);
            this.index = -1;
            this.pointer = 0;
            this.begin = true;
        }
    }

    step() {
        if (!this.begin) return

        this.index += 1;

        let stop = true;
        let pos, char;

        while (this.index < this.tokens.length) {
            [pos, char] = this.tokens[this.index]
            let point = this.array[this.pointer] || 0

            if (char === '>') {
                this.pointer += 1
                if (this.pointer >= this.cell) {
                    throw new Error("pointer out of bounds")
                }
            }

            else if (char === '<') {
                this.pointer -= 1
                if (this.pointer < 0) {
                    throw new Error("pointer out of bounds")
                }
            }

            else if (char === '+') {
                this.array[this.pointer] = (point + 1) % 256
            }

            else if (char === '-') {
                this.array[this.pointer] = (point - 1) % 256
            }

            else if (char === ',') {
                let inp = this.input()
                if (!(Number.isInteger(inp) && 0 <= inp <= 255)) {
                    throw new Error("BFInterpreter() input must be returns unsigned 8-bit integer")
                }
                this.array[this.pointer] = inp
            }

            else if (char === '.') {
                this.output(point)
            }

            else if (char === '[') {
                if (point === 0) {
                    this.index = this.bracket_map[this.index]
                }
            }

            else if (char === ']') {
                if (point !== 0) {
                    this.index = this.bracket_map[this.index]
                }
            }

            stop = false;
            break
        }

        if (stop) {
            this.begin = false;
            return;
        }

        return [this.index, this.pointer, pos, char];
    }
}

export function bf_exec(source) {
    let interpreter = new BFInterpreter(source);
    interpreter.start();
    while (interpreter.begin) {
        interpreter.step();
    }
}