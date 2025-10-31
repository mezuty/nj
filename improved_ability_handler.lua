--[[
    Enhanced Ability Handler Script
    Handles ability input, targeting, and spam prevention
]]

-- Services
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")

-- Player references
local LocalPlayer = Players.LocalPlayer
local Mouse = LocalPlayer:GetMouse()

-- Remote reference
local EventHandler = ReplicatedStorage:WaitForChild("Libraries"):WaitForChild("EventHandler"):WaitForChild("Events"):WaitForChild("Ability")

-- Constants
local MOUSE_TARGET_THRESHOLD = 10 -- Studs threshold for mouse-targeted abilities
local MAX_ABILITY_RANGE = math.huge -- Maximum range for targeting (can be adjusted)

-- State management
local State = {
    abilityKeys = {},
    currentAbility = nil,
    mouseHeld = false,
    keyHeld = {},
    blockedTargets = {},
    immuneTargets = {},
    uiWatchersInitialized = false
}

-- AOE abilities that don't require a target
local AOE_ABILITIES = {
    ["Repulse"] = true,
    ["Area Slam"] = true,
    ["Runes"] = true,
    ["Time Stop"] = true,
    ["Lightning Strike"] = true,
    ["Mass Strangle"] = true,
    ["Teleportation"] = true,
    ["Appa"] = true,
    ["Protego"] = true,
    ["Incendio"] = true,
    ["Shield"] = true,
    ["Hex Bomb"] = true,
    ["Psychic Vortex"] = true,
    ["Psychic Scream"] = true,
    ["Mass Pain"] = true,
    ["Area Blinding"] = true,
    ["Light Barrage"] = true,
    ["Telekinetic Shockwave"] = true,
    ["Telekinetic Stomp"] = true,
    ["Mass Ignite"] = true
}

-- Position-based abilities (use mouse position)
local POSITION_BASED_ABILITIES = {
    ["Appa"] = true,
    ["Teleportation"] = true
}

-- Abilities with special blocking rules
local BLOCKED_BY_ANTIMOVEMENT = {
    ["Pain Infliction"] = true
}

local BLOCKED_BY_IMMUNE = {
    ["Telekinesis"] = true
}

---------------------------------------------------------------------
-- Utility Functions
---------------------------------------------------------------------

local function safeCall(func, ...)
    local success, result = pcall(func, ...)
    if not success then
        warn("Error in ability handler:", result)
        return nil
    end
    return result
end

local function isValidCharacter(character)
    return character and character:FindFirstChild("HumanoidRootPart") ~= nil
end

---------------------------------------------------------------------
-- Ability Key Management
---------------------------------------------------------------------

local function extractAbilityKey(icon)
    local keycode = icon:FindFirstChild("Keycode")
    if not keycode then return nil, nil end
    
    local textLabel = keycode:FindFirstChild("TextLabel")
    if not textLabel then return nil, nil end
    
    local key = string.upper(textLabel.Text)
    local abilityName = icon.Name
    
    return key, abilityName
end

local function refreshAbilityKeys(icons1, icons2)
    local newAbilityKeys = {}
    
    -- Process Icons
    for _, icon in pairs(icons1:GetChildren()) do
        local key, abilityName = extractAbilityKey(icon)
        if key and abilityName then
            newAbilityKeys[key] = abilityName
        end
    end
    
    -- Process Icons2
    for _, icon in pairs(icons2:GetChildren()) do
        local key, abilityName = extractAbilityKey(icon)
        if key and abilityName then
            newAbilityKeys[key] = abilityName
        end
    end
    
    State.abilityKeys = newAbilityKeys
end

local function setupIconWatcher(icon, icons1, icons2)
    local keycode = icon:FindFirstChild("Keycode")
    if not keycode then return end
    
    local textLabel = keycode:FindFirstChild("TextLabel")
    if not textLabel then return end
    
    textLabel:GetPropertyChangedSignal("Text"):Connect(function()
        refreshAbilityKeys(icons1, icons2)
    end)
end

local function setupUIWatchers()
    if State.uiWatchersInitialized then return end
    
    local success, gameInterface = pcall(function()
        return LocalPlayer:WaitForChild("PlayerGui"):WaitForChild("GameInterface")
    end)
    
    if not success then
        warn("Failed to find GameInterface")
        return
    end
    
    local icons1 = gameInterface:WaitForChild("Icons")
    local icons2 = gameInterface:WaitForChild("Icons2")
    
    -- Initial refresh
    refreshAbilityKeys(icons1, icons2)
    
    -- Set up watchers for both Icons containers
    local function setupContainerWatchers(container, icons1, icons2)
        container.ChildAdded:Connect(function()
            refreshAbilityKeys(icons1, icons2)
        end)
        
        container.ChildRemoved:Connect(function()
            refreshAbilityKeys(icons1, icons2)
        end)
        
        -- Set up watchers for existing children
        for _, icon in ipairs(container:GetChildren()) do
            setupIconWatcher(icon, icons1, icons2)
        end
    end
    
    setupContainerWatchers(icons1, icons1, icons2)
    setupContainerWatchers(icons2, icons1, icons2)
    
    State.uiWatchersInitialized = true
end

---------------------------------------------------------------------
-- Target Management
---------------------------------------------------------------------

local function getNearestPlayer()
    if not Mouse.Hit then return nil end
    
    local mousePos = Mouse.Hit.Position
    local nearestPlayer = nil
    local nearestDistance = math.huge
    
    for _, player in ipairs(Players:GetPlayers()) do
        if player == LocalPlayer then continue end
        
        local character = player.Character
        if not isValidCharacter(character) then continue end
        
        local humanoidRootPart = character.HumanoidRootPart
        local distance = (mousePos - humanoidRootPart.Position).Magnitude
        
        if distance < nearestDistance and distance <= MAX_ABILITY_RANGE then
            nearestPlayer = player
            nearestDistance = distance
        end
    end
    
    return nearestPlayer, nearestDistance
end

local function watchTargetStatus(player)
    if player == LocalPlayer then return end
    
    local function monitorCharacter(character)
        if not character then return end
        
        -- Monitor ANTIMovement
        character.ChildAdded:Connect(function(child)
            if child.Name == "ANTIMovement" then
                State.blockedTargets[player.Name] = true
            elseif child.Name == "Immune" and child:IsA("IntValue") then
                State.immuneTargets[player.Name] = child.Value > 0
                
                child:GetPropertyChangedSignal("Value"):Connect(function()
                    State.immuneTargets[player.Name] = child.Value > 0 or nil
                end)
            end
        end)
        
        character.ChildRemoved:Connect(function(child)
            if child.Name == "ANTIMovement" then
                State.blockedTargets[player.Name] = nil
            elseif child.Name == "Immune" then
                State.immuneTargets[player.Name] = nil
            end
        end)
        
        -- Check existing status
        if character:FindFirstChild("ANTIMovement") then
            State.blockedTargets[player.Name] = true
        end
        
        local immuneObj = character:FindFirstChild("Immune")
        if immuneObj and immuneObj:IsA("IntValue") then
            State.immuneTargets[player.Name] = immuneObj.Value > 0 or nil
        end
    end
    
    -- Monitor current character
    if player.Character then
        monitorCharacter(player.Character)
    end
    
    -- Monitor character respawns
    player.CharacterAdded:Connect(monitorCharacter)
end

-- Initialize target watchers
for _, player in ipairs(Players:GetPlayers()) do
    watchTargetStatus(player)
end
Players.PlayerAdded:Connect(watchTargetStatus)

---------------------------------------------------------------------
-- Ability Execution
---------------------------------------------------------------------

local function canTargetAbility(ability, target)
    if not target then return false end
    
    -- Check blocked targets
    if BLOCKED_BY_ANTIMOVEMENT[ability] and State.blockedTargets[target.Name] then
        return false
    end
    
    -- Check immune targets
    if BLOCKED_BY_IMMUNE[ability] and State.immuneTargets[target.Name] then
        return false
    end
    
    return true
end

local function fireAbility(ability)
    if not ability or ability == "Flight" then return end
    
    -- AOE abilities
    if AOE_ABILITIES[ability] then
        local character = LocalPlayer.Character
        if not isValidCharacter(character) then return end
        
        local humanoidRootPart = character.HumanoidRootPart
        
        if POSITION_BASED_ABILITIES[ability] then
            if not Mouse.Hit then return end
            
            local nearestPlayer, distance = getNearestPlayer()
            local targetPosition
            
            if nearestPlayer and distance < MOUSE_TARGET_THRESHOLD then
                targetPosition = nearestPlayer.Character.HumanoidRootPart.Position
            else
                targetPosition = Mouse.Hit.Position
            end
            
            EventHandler:FireServer(ability, targetPosition)
        else
            EventHandler:FireServer(ability, humanoidRootPart.Position)
        end
    else
        -- Targeted abilities
        local target, distance = getNearestPlayer()
        
        if not target or not isValidCharacter(target.Character) then return end
        if not canTargetAbility(ability, target) then return end
        
        local targetHRP = target.Character.HumanoidRootPart
        
        -- Fire the ability
        EventHandler:FireServer(ability, targetHRP.Position, target.Character)
        
        -- Special handling for Telekinesis
        if ability == "Telekinesis" then
            EventHandler:FireServer("Telekinesis", "Click")
        end
    end
end

---------------------------------------------------------------------
-- Input Handling
---------------------------------------------------------------------

UserInputService.InputBegan:Connect(function(input, gameProcessedEvent)
    if gameProcessedEvent then return end
    
    if input.UserInputType == Enum.UserInputType.Keyboard then
        local key = string.upper(input.KeyCode.Name)
        local ability = State.abilityKeys[key]
        
        if ability then
            State.currentAbility = ability
            State.keyHeld[key] = true
            
            -- Fire AOE abilities immediately on key press
            if AOE_ABILITIES[ability] then
                safeCall(fireAbility, ability)
            end
        end
    elseif input.UserInputType == Enum.UserInputType.MouseButton1 then
        if State.currentAbility then
            State.mouseHeld = true
            safeCall(fireAbility, State.currentAbility)
        end
    end
end)

UserInputService.InputEnded:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 then
        State.mouseHeld = false
    elseif input.UserInputType == Enum.UserInputType.Keyboard then
        local key = string.upper(input.KeyCode.Name)
        State.keyHeld[key] = nil
        
        -- Clear current ability if this was the active key
        if State.abilityKeys[key] == State.currentAbility then
            State.currentAbility = nil
        end
    end
end)

---------------------------------------------------------------------
-- Spam Loop (Heartbeat)
---------------------------------------------------------------------

RunService.Heartbeat:Connect(function()
    -- Handle mouse-held abilities
    if State.mouseHeld and State.currentAbility then
        safeCall(fireAbility, State.currentAbility)
    end
    
    -- Handle key-held AOE abilities
    for key, ability in pairs(State.abilityKeys) do
        if State.keyHeld[key] and AOE_ABILITIES[ability] then
            safeCall(fireAbility, ability)
        end
    end
end)

---------------------------------------------------------------------
-- Initialization
---------------------------------------------------------------------

-- Re-hook UI after respawn
LocalPlayer.CharacterAdded:Connect(function()
    State.uiWatchersInitialized = false
    task.defer(setupUIWatchers)
end)

-- Initial setup
task.defer(setupUIWatchers)
