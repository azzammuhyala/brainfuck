local module = {}

module.BFInterpreter = {}

function module.BFInterpreter:new(source, cells, input, output)
    local instance = {}

    setmetatable(instance, self)

    self.__index = self

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

    if type(source) ~= "string" then
        error("BFInterpreter() source must be string")
    end
    if math.type(cells) ~= "integer" and cells ~= nil then
        error("BFInterpreter() cells must be integer")
    end
    if type(input) ~= "function" then
        error("BFInterpreter() input must be a function")
    end
    if type(output) ~= "function" then
        error("BFInterpreter() output must be a function")
    end

    if cells ~= nil and cells <= 0 then
        error("BFInterpreter() cells must be greater than 0")
    end

    self.running = false

    self.source = source
    self.cells = cells
    self.input = input
    self.output = output

    self._tokenIndex = 0
    self._tokens = {}
    self._bracketMap = {}

    local stack = {}
    local comment = false
    local tokenIndex = 1

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

            if character == '[' then
                table.insert(stack, tokenIndex)

            elseif character == ']' then
                if #stack == 0 then
                    error("unbalanced brackets")
                end

                local startIndex = table.remove(stack)

                self._bracketMap[startIndex] = tokenIndex
                self._bracketMap[tokenIndex] = startIndex
            end

            table.insert(self._tokens, {position, character})
            tokenIndex = tokenIndex + 1
        end
    end

    if #stack ~= 0 then
        error("unbalanced brackets")
    end

    return instance
end

function module.BFInterpreter:start()
    if self.running then
        return
    end

    self._tokenIndex = 0

    self.running = true
    self.memory = {}
    self.point = 1

    if self.cells ~= nil then
        for i = 1, self.cells do
            self.memory[i] = 0
        end
    end
end

function module.BFInterpreter:step()
    if not self.running then
        return
    end

    self._tokenIndex = self._tokenIndex + 1

    if self._tokenIndex > #self._tokens then
        self.running = false
        return
    end

    local position, character = table.unpack(self._tokens[self._tokenIndex])
    local dataPointer = self.memory[self.point] or 0

    if character == '>' then
        self.point = self.point + 1
        if self.cells == nil then
            if self.point > #self.memory then
                self.memory[self.point] = 0
            end
        elseif self.point > self.cells then
            error("pointer out of bounds")
        end

    elseif character == '<' then
        if self.point == 1 then
            error("pointer out of bounds")
        end
        self.point = self.point - 1

    elseif character == '+' then
        self.memory[self.point] = (dataPointer + 1) % 256

    elseif character == '-' then
        self.memory[self.point] = (dataPointer - 1) % 256

    elseif character == ',' then
        local input = self.input()

        if not (math.type(input) == "integer" and input >= 0 and input <= 255) then
            error("BFInterpreter() input must be returns unsigned 8-bit integer")
        end

        self.memory[self.point] = input

    elseif character == '.' then
        self.output(dataPointer)

    elseif character == '[' and dataPointer == 0 then
        self._tokenIndex = self._bracketMap[self._tokenIndex]

    elseif character == ']' and dataPointer ~= 0 then
        self._tokenIndex = self._bracketMap[self._tokenIndex]
    end

    return {self.point, position, character}
end

function module.BFInterpreter:stop(cleanUp)
    if not self.running then
        return
    end

    self.running = false

    if cleanUp == nil or cleanUp then
        self.memory = nil
        self.point = nil
    end
end

function module.BFExec(source, cells, input, output)
    local interpreter = module.BFInterpreter:new(source, cells, input, output)

    interpreter:start()

    repeat interpreter:step() until not interpreter.running

    interpreter:stop()
end

return module