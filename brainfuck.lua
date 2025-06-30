local module = {}

module.BF_DEFAULT_CELL = 30000

function module.BFTokens(source)
    if type(source) ~= "string" then
        error("bf_tokens() source must be string")
    end

    local comment = false
    local tokens = {}

    for position = 1, #source do
        local character = source:sub(position, position)

        if not comment and character == '#' then
            comment = true
        elseif comment and character == '\n' then
            comment = false
        end

        if not comment and (
            character == '<' or
            character == '>' or
            character == '+' or
            character == '-' or
            character == '.' or
            character == ',' or
            character == '[' or
            character == ']'
        ) then
            table.insert(tokens, {position, character})
        end
    end

    return tokens
end

module.BFInterpreter = {}

function module.BFInterpreter:new(source, cell, input, output)
    local instance = {}

    setmetatable(instance, self)

    self.__index = self

    if cell == nil then
        cell = module.BF_DEFAULT_CELL
    end

    if input == nil then
        function input()
            while true do
                local result = string.byte(io.read(1))
                if math.type(result) == "integer" and result >= 0 and result <= 255 then
                    return result
                end
            end
        end
    end

    if output == nil then
        function output(byte)
            io.write(string.char(byte))
            io.flush()
        end
    end

    if math.type(cell) ~= "integer" or cell <= 0 then
        error("BFInterpreter() cell must be integer and greater than 0")
    end
    if not type(input) == "function" then
        error("BFInterpreter() input must be a function")
    end
    if not type(output) == "function" then
        error("BFInterpreter() output must be a function")
    end

    self.tokens = module.BFTokens(source)
    self.cell = cell
    self.input = input
    self.output = output

    self.begin = false
    self.bracketMap = {}

    local stack = {}

    for i = 1, #self.tokens do
        local character = self.tokens[i][2]

        if character == '[' then
            table.insert(stack, i)

        elseif character == ']' then
            if #stack == 0 then
                error("unbalanced brackets")
            end

            local startIndex = table.remove(stack)

            self.bracketMap[startIndex] = i
            self.bracketMap[i] = startIndex
        end
    end

    if #stack ~= 0 then
        error("unbalanced brackets")
    end

    return instance
end

function module.BFInterpreter:start()
    if self.begin then return end

    self.memory = {}
    self.index = 0
    self.pointer = 1
    self.begin = true
end

function module.BFInterpreter:step()
    if not self.begin then return end

    self.index = self.index + 1

    local stop = true
    local position, character

    while self.index <= #self.tokens do
        local point = self.memory[self.pointer] or 0

        position, character = table.unpack(self.tokens[self.index])

        if character == '>' then
            self.pointer = self.pointer + 1
            if self.pointer > self.cell then
                error("pointer out of bounds")
            end

        elseif character == '<' then
            self.pointer = self.pointer - 1
            if self.pointer < 1 then
                error("pointer out of bounds")
            end

        elseif character == '+' then
            self.memory[self.pointer] = (point + 1) % 256

        elseif character == '-' then
            self.memory[self.pointer] = (point - 1) % 256

        elseif character == ',' then
            local input = self.input()

            if not (math.type(input) == "integer" and input >= 0 and input <= 255) then
                error("BFInterpreter() input must be returns unsigned 8-bit integer")
            end

            self.memory[self.pointer] = input

        elseif character == '.' then
            self.output(point)

        elseif character == '[' then
            if point == 0 then
                self.index = self.bracketMap[self.index]
            end

        elseif character == ']' then
            if point ~= 0 then
                self.index = self.bracketMap[self.index]
            end

        end

        stop = false
        break
    end

    if stop then
        self.begin = false
        return
    end

    return {self.index, self.pointer, position, character}
end

function module.BFInterpreter:stop()
    self.begin = false
end

function module.BFExec(source, cell, input, output)
    local interpreter = module.BFInterpreter:new(source, cell, input, output)
    interpreter:start()
    repeat interpreter:step() until not interpreter.begin
end

return module