const validBFCharacters = ['>', '<', '+', '-', '.', ',', '[', ']'];

export class BFInterpreter {

    constructor (source, cells=null, input=null, output=null) {
        if (input === null) {
            input = () => {
                while (true) {
                    let result = prompt("Brainfuck input (1 character): ");
                    if (result === null) {
                        return 0;
                    }
                    else if (typeof result === 'string') {
                        result = result.charCodeAt(0);
                        if (Number.isInteger(result) && result >= 0 && result <= 255) {
                            return result;
                        }
                    }
                }
            }
        }

        if (output === null) {
            output = (byte) => {
                console.log(String.fromCharCode(byte));
            }
        }

        if (typeof source !== 'string') {
            throw new Error("BFInterpreter() source must be string");
        }
        if (!Number.isInteger(cells) && cells !== null) {
            throw new Error("BFInterpreter() cells must be integer");
        }
        if (typeof input !== 'function') {
            throw new Error("BFInterpreter() input must be function");
        }
        if (typeof output !== 'function') {
            throw new Error("BFInterpreter() output must be function");
        }

        if (cells !== null && cells <= 0) {
            throw new Error("BFInterpreter() cells must be integer and greater than 0");
        }

        this.running = false;

        this.source = source;
        this.cells = cells;
        this.input = input;
        this.output = output;

        this._tokenIndex = -1;
        this._tokens = [];
        this._bracketMap = {};

        let stack = [];
        let comment = false;
        let tokenIndex = 0;

        for (let position = 0; position < source.length; position++) {
            let character = source[position];

            if (!comment && character === '#') {
                comment = true;
            }
            else if (comment && character === '\n') {
                comment = false;
            }

            if (!comment && validBFCharacters.includes(character)) {
                if (character === '[') {
                    stack.push(tokenIndex);
                }

                else if (character === ']') {
                    if (stack.length === 0) {
                        throw new SyntaxError("unbalanced brackets");
                    }

                    let startIndex = stack.pop();

                    this._bracketMap[startIndex] = tokenIndex;
                    this._bracketMap[tokenIndex] = startIndex;
                }

                this._tokens.push([position, character]);
                tokenIndex++;
            }
        }

        if (stack.length !== 0) {
            throw new SyntaxError("unbalanced brackets");
        }
    }

    start() {
        if (this.running) return;

        this._tokenIndex = -1;

        this.running = true;
        this.memory = this.cells === null ? [0] : new Array(this.cells).fill(0);
        this.point = 0;
    }

    step() {
        if (!this.running) return;

        this._tokenIndex++;

        if (this._tokenIndex >= this._tokens.length) {
            this.running = false;
            return;
        }

        let [position, character] = this._tokens[this._tokenIndex];
        let dataPointer = this.memory[this.point] || 0;

        if (character === '>') {
            this.point++;
            if (this.cells === null) {
                if (this.point == this.memory.length) {
                    this.memory.push(0);
                }
            }
            else if (this.point >= this.cells) {
                throw new RangeError("pointer out of bounds");
            }
        }

        else if (character === '<') {
            if (this.point === 0) {
                throw new RangeError("pointer out of bounds");
            }
            this.point--;
        }

        else if (character === '+') {
            this.memory[this.point] = (dataPointer + 1) % 256;
        }

        else if (character === '-') {
            this.memory[this.point] = (dataPointer - 1) % 256;
        }

        else if (character === ',') {
            let input = this.input();

            if (!(Number.isInteger(input) && input >= 0 && input <= 255)) {
                throw new TypeError("BFInterpreter() input must be returns unsigned 8-bit integer");
            }

            this.memory[this.point] = input;
        }

        else if (character === '.') {
            this.output(dataPointer);
        }

        else if (character === '[' && dataPointer === 0) {
            this._tokenIndex = this._bracketMap[this._tokenIndex];
        }
        
        else if (character === ']' && dataPointer !== 0) {
            this._tokenIndex = this._bracketMap[this._tokenIndex];
        }

        return [this.point, position, character];
    }

    stop(cleanUp=true) {
        if (!this.running) return;

        this.running = false;

        if (cleanUp) {
            this.memory = undefined;
            this.point = undefined;
        }
    }
}

export function BFExec(source, cells=null, input=null, output=null) {
    let interpreter = new BFInterpreter(source, cells, input, output);

    interpreter.start();

    while (interpreter.running) interpreter.step();

    interpreter.stop();
}