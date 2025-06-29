local module = {}

module.BF_DEFAULT_CELL = 30000

function module.bf_tokens(source)
    local comment = false
    local tokens = {}

    for index = 1, #source do
        local char = source:sub(index, index)

        if not comment and char == '#' then
            comment = true
        elseif comment and char == '\n' then
            comment = false
        end

        if not comment and (
            char == '<' or
            char == '>' or
            char == '+' or
            char == '-' or
            char == '.' or
            char == ',' or
            char == '[' or
            char == ']'
        ) then
            table.insert(tokens, {index, char})
        end
    end

    return tokens
end

module.BFInterpreter = {}
module.BFInterpreter.__index = module.BFInterpreter

function module.BFInterpreter:new(source, cell, input, output)
    local self = setmetatable({}, module.BFInterpreter)

    if cell == nil then
        cell = module.BF_DEFAULT_CELL
    end

    if input == nil then
        function input()
            return string.byte(io.read(1))
        end
    end

    if output == nil then
        function output(str)
            io.write(string.char(str))
            io.flush()
        end
    end

    if type(cell) ~= "number" or cell <= 0 then
        error("BFInterpreter() cell must be integer and greather than 0")
    end
    if not type(input) == "function" then
        error("BFInterpreter() input must be a function")
    end
    if not type(output) == "function" then
        error("BFInterpreter() output must be a function")
    end

    self.tokens = module.bf_tokens(source)
    self.cell = cell
    self.input = input
    self.output = output

    self.begin = false
    self.bracket_map = {}

    local stack = {}

    for i = 1, #self.tokens do
        local token = self.tokens[i]
        local char = token[2]

        if char == '[' then
            table.insert(stack, i)
        elseif char == ']' then
            if #stack == 0 then
                error("unbalanced brackets")
            end

            local start_index = table.remove(stack)

            self.bracket_map[start_index] = i
            self.bracket_map[i] = start_index
        end
    end

    if #stack ~= 0 then
        error("unbalanced brackets")
    end

    return self
end

function module.BFInterpreter:inter()
    if not self.begin then
        self.array = {}
        self.index = 0
        self.pointer = 1
        self.begin = true
    end
    return self
end

function module.BFInterpreter:next()
    if not self.begin then
        return
    end

    local stop = true
    local pos, char

    self.index = self.index + 1

    while self.index <= #self.tokens do
        local token = self.tokens[self.index]
        local point = self.array[self.pointer] or 0

        pos = token[1]
        char = token[2]

        if char == '>' then
            self.pointer = self.pointer + 1

            if self.pointer > self.cell then
                error("pointer out of range")
            end

        elseif char == '<' then
            self.pointer = self.pointer - 1

            if self.pointer < 1 then
                error("pointer out of range")
            end

        elseif char == '+' then
            self.array[self.pointer] = (point + 1) % 256

        elseif char == '-' then
            self.array[self.pointer] = (point - 1) % 256

        elseif char == ',' then
            local inp = self.input()

            if not (type(inp) == "number" and 0 <= inp <= 255) then
                error("BFInterpreter() input must be returns unsigned 8-bit integer")
            end

            self.array[self.pointer] = inp

        elseif char == '.' then
            self.output(point)

        elseif char == '[' then
            if point == 0 then
                self.index = self.bracket_map[self.index]
            end

        elseif char == ']' then
            if point ~= 0 then
                self.index = self.bracket_map[self.index]
            end

        end

        stop = false
        break
    end

    if stop then
        self.begin = false
        return
    end

    return {self.index, self.pointer, pos, char}
end

function module.bf_exec(source, cell, input, output)
    local interpreter = module.BFInterpreter:new(source, cell, input, output)
    interpreter:inter()
    repeat interpreter:next() until not interpreter.begin
end

return module