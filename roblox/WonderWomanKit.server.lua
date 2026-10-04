local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Debris = game:GetService("Debris")
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local ServerScriptService = game:GetService("ServerScriptService")

local MoveLock = require(ReplicatedStorage.Modules:WaitForChild("MoveLock"))
local CombatRules = require(ReplicatedStorage.Modules:WaitForChild("CombatRules"))
local AnimationManager = require(ReplicatedStorage.Modules:WaitForChild("AnimationManager"))
local CharacterIndex = require(ReplicatedStorage.Modules:WaitForChild("IvyCharacterIndex"))
local CraterModule
pcall(function()
	CraterModule = require(ReplicatedStorage.Modules:WaitForChild("CraterModule"))
end)

local coinDamage = ServerScriptService:WaitForChild("CoinDamage")
local screenShakeEvent = ReplicatedStorage.GlobalRemotes:WaitForChild("ScreenShakeEvent")
local clientVFXEvent = ReplicatedStorage.GlobalRemotes:WaitForChild("ClientVFXEvent")
local remoteEvent = ReplicatedStorage.AbilityRemotes:WaitForChild("WonderWomanKitEvent")
local library = ReplicatedStorage:WaitForChild("VFX"):WaitForChild("WonderWomanVFX")

local effectsFolder = workspace:FindFirstChild("Effects")
if not effectsFolder then
	effectsFolder = Instance.new("Folder")
	effectsFolder.Name = "Effects"
	effectsFolder.Parent = workspace
end
if not CollectionService:HasTag(effectsFolder, "RockModuleIgnore") then
	CollectionService:AddTag(effectsFolder, "RockModuleIgnore")
end

local UP = Vector3.yAxis
local AMAZON_GOLD = Color3.fromRGB(255, 186, 64)
local TRUTH_GOLD = Color3.fromRGB(255, 214, 120)
local ZEUS_BLUE = Color3.fromRGB(120, 196, 255)
local GLOW_FILL = Color3.fromRGB(255, 192, 76)
local GLOW_OUTLINE = Color3.fromRGB(255, 242, 206)
local ZEUS_FILL = Color3.fromRGB(110, 190, 255)
local ZEUS_OUTLINE = Color3.fromRGB(226, 244, 255)
local AOE_HEIGHT = 14
local RANGE_TOLERANCE = 10
local MAX_ABILITY_LIFETIME = 20
local COOLDOWN_GRACE = 0.06
local STOMP_BASE = 40
local SNARE_BASE = 8.3
local WAVE_BASE = 26

local ROPE_LINE_NODES = 14
local ROPE_LOOP_NODES = 14
local ROPE_ITERATIONS = 12
local ROPE_GRAVITY = Vector3.new(0, -72, 0)
local ROPE_DAMPING = 0.972
local ROPE_MAX_STEP = 3.5

local SOUNDS = {
	Swing = "rbxassetid://6241709963",
	Woosh = "rbxassetid://117297744119258",
	Ribbon = "rbxassetid://9126229280",
	Charge = "rbxassetid://9125959352",
	Impact = "rbxassetid://9125402735",
	Slam = "rbxassetid://71472197762839",
	RockBreak = "rbxassetid://9118612945",
	Landing = "rbxassetid://128343381193523",
	SonicBoom = "rbxassetid://9120769331",
	Boom = "rbxassetid://6290067239",
	Transform = "rbxassetid://3365120869",
	Absorb = "rbxassetid://182765513",
	Whisper = "rbxassetid://9126214616",
	Thunder = "rbxassetid://6409267922",
	Bolt = "rbxassetid://168586586",
	Zap = "rbxassetid://9126069007",
	ZapCharge = "rbxassetid://135895192563038",
	Current = "rbxassetid://8323014538",
}

local ANIMS = {
	Grip = "82577704372190",
	Throw = "104698026340651",
	Charm = "140017608581659",
	Spore = "106972392816455",
	Pain = "74544533292035",
	Whip = "114833487934602",
	Slam = "106320106414632",
	Bind = "139036230700742",
}

-- Wonder Woman animation slots: replace these IDs with her custom animations when they are ready.
-- Every ability is ONE animation (played once at cast start, speed 1). Victim is the target's hit reaction.
local WW_ANIMS = {
	LassoLash = ANIMS.Whip, -- paste the exported WonderWoman_LassoLash ID here
	LassoOfTruth = ANIMS.Charm, -- paste the exported WonderWoman_LassoOfTruth ID here
	HestiasSnare = ANIMS.Bind, -- paste the exported WonderWoman_HestiasSnare ID here
	BraceletClash = ANIMS.Spore, -- paste the exported WonderWoman_BraceletClash ID here
	Godkiller = ANIMS.Slam, -- paste the exported WonderWoman_Godkiller ID here
	GoldenEagle = ANIMS.Spore, -- paste the exported WonderWoman_GoldenEagle ID here
	WrathOfZeus = ANIMS.Throw, -- paste the exported WonderWoman_WrathOfZeus ID here
	Victim = ANIMS.Pain,
}

local ABILITY_CONFIG = {
	LassoLash = {
		flightAllowed = true, targetKind = "Vector3",
		cooldown = 1.5, range = 34, castTime = 0.28, minReach = 8,
		crackTime = 0.2, recoilTime = 0.32, lineRadius = 3.2, tipRadius = 5,
		damage = 16, tipDamage = 10, knockback = 10, tipKnockback = 26, tipLift = 9,
		ragdoll = 1,
	},
	LassoOfTruth = {
		flightAllowed = true, targetKind = "Instance", armorOnLand = true,
		cooldown = 14, range = 55, castTime = 0.45,
		spinSpeed = 16, loopRadius = 2.6, throwTime = 0.35,
		dropHeight = 3.2, cinchTime = 0.18, bindRadius = 1.25, auraScale = 0.75,
		reelTime = 0.45, reelGap = 5.5, compelTime = 0.9, tickInterval = 0.3, tickDamage = 4,
		hurlTime = 0.42, slamHeight = 13, slamBack = 7,
		slamDamage = 26, ragdoll = 1.8, bounce = 16, craterRadius = 6,
	},
	HestiasSnare = {
		flightAllowed = true, targetKind = "Vector3", armorOnLand = true,
		cooldown = 18, range = 60, radius = 14, castTime = 0.5,
		spinSpeed = 14, spinRadius = 3.2, throwTime = 0.4, throwHeight = 7,
		dropTime = 0.14, cinchTime = 0.6, cinchRadius = 3.2, spacing = 1.6, tickDamage = 5,
		bindTime = 0.3, liftHeight = 10, liftTime = 0.28, slamTime = 0.16,
		slamDamage = 30, knockback = 20, lift = 18, ragdoll = 1.8,
	},
	BraceletClash = {
		flightAllowed = true, targetKind = "Vector3",
		cooldown = 16, castTime = 0.55, radius = 20,
		damage = 30, knockback = 52, lift = 22, ragdoll = 1.8,
	},
	Godkiller = {
		flightAllowed = true, targetKind = "Vector3",
		cooldown = 12, range = 40, minDash = 14, castTime = 0.18,
		dashSpeed = 160, dashTime = 0.22, contactRadius = 4.5, missCooldownScale = 0.4, contactDamage = 6,
		passDistance = 7, passTime = 0.12, stillTime = 0.5,
		cutTilts = {0.55, -0.7, 1.35, -0.25}, cutGap = 0.1, cutDamage = 5, slashScale = 0.6,
		fissureTime = 0.22, pillarScale = 2.2, pillarRing = 12, pillarDamage = 24, pillarLift = 55, ragdoll = 2.4,
	},
	GoldenEagle = {
		flightAllowed = true, targetKind = "Vector3", unstoppable = true,
		cooldown = 14, range = 60, castTime = 0.4,
		wingScale = 0.62, foldAngle = 1.25, flapAngle = 0.28,
		hoverHeight = 3, riseTime = 0.25, descendTime = 0.25, foldTime = 0.22, fireTime = 1.25,
		feathers = 10, stagger = 0.055, speed = 130, minTravel = 0.18, maxTravel = 0.6, spread = 0.42,
		homingRadius = 9, hitRadius = 2.8, featherDamage = 3.5, slow = 0.7, slowTime = 0.8,
		bigDamage = 14, bigKnockback = 34, bigLift = 12, bigRagdoll = 1,
	},
	WrathOfZeus = {
		flightAllowed = true, targetKind = "Instance", unstoppable = true,
		cooldown = 32, range = 60, castTime = 0.35,
		riseHeight = 4, riseTime = 0.35, strikes = 3, strikeGap = 0.33,
		torrentTime = 1.3, tickInterval = 0.19, tickDamage = 5, beamScale = 0.5,
		chainRadius = 16, chainCount = 3, chainDamage = 2.5, chainScale = 0.22,
		finaleDamage = 36, ragdoll = 2.2, knockback = 18, lift = 30,
		splashRadius = 16, splashDamage = 16, splashKnockback = 34, splashLift = 18, splashRagdoll = 1.4,
		descendTime = 0.35,
	},
}

local activeAbilities = {}
local cooldowns = {}
local abilityInstanceCounter = 0
local slowCounter = 0
local truthCounter = 0
local groundFilterCache, groundFilterStamp = nil, 0

local function getGroundFilter()
	local now = os.clock()
	if groundFilterCache and now - groundFilterStamp < 0.25 then
		return groundFilterCache
	end
	local filter = {effectsFolder}
	for _, child in ipairs(workspace:GetChildren()) do
		if child:FindFirstChildOfClass("Humanoid") then
			table.insert(filter, child)
		end
	end
	for _, tagged in ipairs(CollectionService:GetTagged("RockModuleIgnore")) do
		table.insert(filter, tagged)
	end
	local interactables = workspace:FindFirstChild("Interactables")
	local lamps = interactables and interactables:FindFirstChild("StreetLights")
	if lamps then
		for _, item in ipairs(lamps:GetDescendants()) do
			if item:IsA("BasePart") and item.Name == "GlassShatter" then
				table.insert(filter, item)
			end
		end
	end
	groundFilterCache = filter
	groundFilterStamp = now
	return filter
end

local function groundParams(extra)
	local filter = table.clone(getGroundFilter())
	if extra then
		table.insert(filter, extra)
	end
	local params = RaycastParams.new()
	params.FilterDescendantsInstances = filter
	params.FilterType = Enum.RaycastFilterType.Exclude
	return params
end

local function getGroundPosition(position, extra)
	local hit = workspace:Raycast(position + UP * 6, Vector3.new(0, -80, 0), groundParams(extra))
	return hit and hit.Position or position
end

local function findFloor(position, extra)
	local hit = workspace:Raycast(position, Vector3.new(0, -300, 0), groundParams(extra))
	return hit and hit.Position or nil
end

local function flatDirection(from, to, fallback)
	local delta = Vector3.new(to.X - from.X, 0, to.Z - from.Z)
	if delta.Magnitude > 0.05 then
		return delta.Unit
	end
	if fallback then
		local flat = Vector3.new(fallback.X, 0, fallback.Z)
		if flat.Magnitude > 0.05 then
			return flat.Unit
		end
	end
	return Vector3.new(0, 0, -1)
end

local function isCharacterValid(character)
	if not character or not character.Parent then return false end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local rootPart = character:FindFirstChild("HumanoidRootPart")
	return humanoid ~= nil and rootPart ~= nil and humanoid.Health > 0
end

local function flagOn(character, flagName)
	local value = character:FindFirstChild(flagName)
	return (value ~= nil and value:IsA("BoolValue") and value.Value) or character:GetAttribute(flagName) == true
end

local function setCharacterFlag(character, flagName, state)
	if not character or not character.Parent then return end
	local flag = character:FindFirstChild(flagName)
	if not flag then
		flag = Instance.new("BoolValue")
		flag.Name = flagName
		flag.Parent = character
	end
	if flag:IsA("BoolValue") then
		flag.Value = state
	end
end

local function canCast(character)
	if not isCharacterValid(character) then return false end
	if flagOn(character, "Ragdoll") or flagOn(character, "Ragdolled") or flagOn(character, "BeingAttacked") then return false end
	if character:GetAttribute("Silenced") or character:GetAttribute("CirceForm") then return false end
	return true
end

local function canBeHit(target)
	if not isCharacterValid(target) then return false end
	if target:IsDescendantOf(effectsFolder) then return false end
	return CombatRules.canDamage(target)
end

local function canBeAffected(target)
	return canBeHit(target) and CombatRules.canGrab(target)
end

local function canBeGrabbed(target)
	return canBeHit(target) and CombatRules.canControl(target)
end

local function captureBaseStats(character)
	local hum = character and character:FindFirstChildOfClass("Humanoid")
	if not hum then return nil end
	if character:GetAttribute("BaseWalkSpeed") == nil and hum.WalkSpeed > 0 then
		character:SetAttribute("BaseWalkSpeed", hum.WalkSpeed)
	end
	if character:GetAttribute("BaseJumpHeight") == nil and hum.JumpHeight > 0 then
		character:SetAttribute("BaseJumpHeight", hum.JumpHeight)
	end
	if character:GetAttribute("BaseJumpPower") == nil and hum.JumpPower > 0 then
		character:SetAttribute("BaseJumpPower", hum.JumpPower)
	end
	return hum
end

local function restoreStats(character)
	local hum = character and character:FindFirstChildOfClass("Humanoid")
	if not hum then return end
	if MoveLock.isLocked(character) then
		MoveLock.refresh(character)
		return
	end
	hum.WalkSpeed = character:GetAttribute("BaseWalkSpeed") or 16
	hum.JumpHeight = character:GetAttribute("BaseJumpHeight") or 7.2
	hum.JumpPower = character:GetAttribute("BaseJumpPower") or 50
	hum.AutoRotate = true
	if not flagOn(character, "Ragdoll") then
		hum.PlatformStand = false
	end
end

local function applySlow(character, multiplier, duration)
	local hum = captureBaseStats(character)
	if not hum then return end
	slowCounter += 1
	local lockId = "WonderWomanSlow_" .. slowCounter
	MoveLock.apply(character, lockId, {factor = multiplier, allowJump = true, allowRotate = true, duration = duration + 1})
	task.delay(duration, function()
		MoveLock.release(character, lockId)
		if character.Parent and hum.Health > 0 then
			restoreStats(character)
		end
	end)
end

local function isInsideArea(position, origin, radius)
	local delta = position - origin
	if math.abs(delta.Y) > AOE_HEIGHT then return false end
	return Vector3.new(delta.X, 0, delta.Z).Magnitude <= radius
end

local function launch(root, velocity, data)
	if not root or not root.Parent or root.Anchored then return end
	if not CombatRules.canControl(root.Parent, data and data.targetLockId) then return end
	root.AssemblyLinearVelocity = velocity
end

local function stabilizeCharacter(character, lookAt)
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	root.AssemblyLinearVelocity = Vector3.zero
	root.AssemblyAngularVelocity = Vector3.zero
	local look = typeof(lookAt) == "Vector3" and flatDirection(root.Position, lookAt, root.CFrame.LookVector) or flatDirection(root.Position, root.Position, root.CFrame.LookVector)
	root.CFrame = CFrame.lookAt(root.Position, root.Position + look)
end

local function standHeight(character)
	local root = character:FindFirstChild("HumanoidRootPart")
	local hum = character:FindFirstChildOfClass("Humanoid")
	if not (root and hum) then return 3 end
	return root.Size.Y * 0.5 + hum.HipHeight
end

local function torsoOf(character)
	local torso = character:FindFirstChild("UpperTorso")
	if torso and torso:IsA("BasePart") then
		return torso
	end
	return character:FindFirstChild("HumanoidRootPart")
end

local function shakeCharacter(character, magnitude, roughness, fadeIn, fadeOut)
	local plr = Players:GetPlayerFromCharacter(character)
	if plr then
		screenShakeEvent:FireClient(plr, magnitude, roughness, fadeIn, fadeOut)
	end
end

local function shakeArea(position, radius, magnitude, roughness, fadeIn, fadeOut)
	for _, plr in ipairs(Players:GetPlayers()) do
		local char = plr.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		if root then
			local distance = (root.Position - position).Magnitude
			if distance <= radius then
				local scale = 1 - math.clamp(distance / radius, 0, 1) * 0.8
				screenShakeEvent:FireClient(plr, magnitude * scale, roughness, fadeIn, fadeOut)
			end
		end
	end
end

local function applyTargetScreenEffect(character, duration, color)
	local plr = Players:GetPlayerFromCharacter(character)
	if plr then
		clientVFXEvent:FireClient(plr, "TargetScreenEffect", duration or 1.2, color or AMAZON_GOLD)
	end
end

local function flashArea(position)
	clientVFXEvent:FireAllClients("ScreenFlash", position)
end

local function isOnCooldown(userId, abilityName)
	local player = Players:GetPlayerByUserId(userId)
	if player and player:GetAttribute("CooldownsDisabled") then return false end
	local perUser = cooldowns[userId]
	local readyAt = perUser and perUser[abilityName]
	return readyAt ~= nil and os.clock() < (readyAt - COOLDOWN_GRACE)
end

local function startCooldown(userId, abilityName)
	local player = Players:GetPlayerByUserId(userId)
	if player and player:GetAttribute("CooldownsDisabled") then return end
	local cfg = ABILITY_CONFIG[abilityName]
	if not cfg or not cfg.cooldown then return end
	cooldowns[userId] = cooldowns[userId] or {}
	cooldowns[userId][abilityName] = os.clock() + cfg.cooldown
end

local function sendCooldownSnapshot(player)
	local perUser = cooldowns[player.UserId]
	if not perUser then return end
	local now = os.clock()
	local remaining, any = {}, false
	for abilityName, readyAt in pairs(perUser) do
		local left = readyAt - now
		if left > 0.1 then
			remaining[abilityName] = left
			any = true
		else
			perUser[abilityName] = nil
		end
	end
	if any then
		remoteEvent:FireClient(player, "CooldownSync", remaining)
	end
end

local function isInRange(casterChar, abilityName, targetData)
	local cfg = ABILITY_CONFIG[abilityName]
	if not cfg or not cfg.range then return true end
	local root = casterChar:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local point
	if typeof(targetData) == "Vector3" then
		point = targetData
	elseif typeof(targetData) == "Instance" then
		local targetRoot = targetData:FindFirstChild("HumanoidRootPart")
		if not targetRoot then return false end
		point = targetRoot.Position
	else
		return false
	end
	local delta = point - root.Position
	return Vector3.new(delta.X, 0, delta.Z).Magnitude <= cfg.range + RANGE_TOLERANCE
end

local function all(instance)
	local list = instance:GetDescendants()
	table.insert(list, instance)
	return list
end

local function gracefullyCleanupVFX(instance)
	if not instance or not instance.Parent then return end
	if instance:GetAttribute("WonderWomanFading") then return end
	instance:SetAttribute("WonderWomanFading", true)
	local maxLifetime = 0.5
	local info = TweenInfo.new(0.35, Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
	for _, item in ipairs(all(instance)) do
		if item:IsA("ParticleEmitter") then
			item.Enabled = false
			maxLifetime = math.max(maxLifetime, item.Lifetime.Max)
		elseif item:IsA("Beam") or item:IsA("Trail") then
			item.Enabled = false
			if item:IsA("Trail") then
				maxLifetime = math.max(maxLifetime, item.Lifetime)
			end
		elseif item:IsA("Light") then
			TweenService:Create(item, info, {Brightness = 0}):Play()
		elseif item:IsA("Highlight") then
			TweenService:Create(item, info, {FillTransparency = 1, OutlineTransparency = 1}):Play()
		elseif item:IsA("Decal") or item:IsA("Texture") then
			if item.Transparency < 1 then
				TweenService:Create(item, info, {Transparency = 1}):Play()
			end
		elseif item:IsA("BasePart") then
			if item.Transparency < 1 then
				TweenService:Create(item, info, {Transparency = 1}):Play()
			end
		elseif item:IsA("Sound") then
			TweenService:Create(item, info, {Volume = 0}):Play()
		end
	end
	Debris:AddItem(instance, math.max(3, math.min(maxLifetime + 0.4, 8)))
end

local function glowPulse(adornee, fadeIn, hold, fadeOut, fill, outline)
	if not adornee or not adornee.Parent then return nil end
	local highlight = Instance.new("Highlight")
	highlight.Name = "WonderWomanGlow"
	highlight.Adornee = adornee
	highlight.DepthMode = Enum.HighlightDepthMode.Occluded
	highlight.FillColor = fill or GLOW_FILL
	highlight.OutlineColor = outline or GLOW_OUTLINE
	highlight.FillTransparency = 1
	highlight.OutlineTransparency = 1
	highlight.Parent = effectsFolder
	TweenService:Create(highlight, TweenInfo.new(math.max(fadeIn, 0.01), Enum.EasingStyle.Quad, Enum.EasingDirection.In), {FillTransparency = 0.6, OutlineTransparency = 0.15}):Play()
	task.delay(fadeIn + hold, function()
		if not highlight.Parent then return end
		TweenService:Create(highlight, TweenInfo.new(math.max(fadeOut, 0.01), Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {FillTransparency = 1, OutlineTransparency = 1}):Play()
		Debris:AddItem(highlight, fadeOut + 0.1)
	end)
	return highlight
end

local function flashLights(instance, duration)
	for _, item in ipairs(all(instance)) do
		if item:IsA("Light") then
			item.Enabled = true
			item.Brightness = math.min(item.Brightness, 2)
			TweenService:Create(item, TweenInfo.new(duration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Brightness = 0}):Play()
		end
	end
end

local function enableAll(instance, skipName)
	if not instance then return end
	for _, item in ipairs(all(instance)) do
		local skipped = skipName ~= nil and (item.Name == skipName or (item.Parent ~= nil and item.Parent.Name == skipName))
		if not skipped then
			if item:IsA("ParticleEmitter") or item:IsA("Beam") or item:IsA("Trail") then
				item.Enabled = true
			elseif item:IsA("Light") then
				item.Enabled = true
				item.Brightness = math.min(item.Brightness, 2)
			end
		end
	end
end

local function prepPart(part)
	part.CanCollide = false
	part.CanTouch = false
	part.CanQuery = false
	part.Massless = true
	part.CastShadow = false
end

local function spawnAsset(source, cframe, scale, keepRotation)
	if not source then return nil end
	local clone = source:Clone()
	local model
	if clone:IsA("Model") then
		model = clone
	else
		model = Instance.new("Model")
		model.Name = source.Name
		clone.Parent = model
		if clone:IsA("BasePart") then
			clone.PivotOffset = CFrame.identity
			model.PrimaryPart = clone
		end
	end
	for _, item in ipairs(model:GetDescendants()) do
		if item:IsA("LuaSourceContainer") then
			item:Destroy()
		elseif item:IsA("BasePart") then
			prepPart(item)
			item.Anchored = true
		elseif item:IsA("ParticleEmitter") or item:IsA("Beam") or item:IsA("Trail") then
			item.Enabled = false
		end
	end
	if scale and scale ~= 1 then
		model:ScaleTo(model:GetScale() * scale)
	end
	local rotation = CFrame.identity
	if keepRotation then
		rotation = source:IsA("BasePart") and source.CFrame.Rotation or source:GetPivot().Rotation
	end
	model:PivotTo(cframe * rotation)
	CollectionService:AddTag(model, "RockModuleIgnore")
	model.Parent = effectsFolder
	return model
end

local function setModelScale(model, value)
	local scale = math.max(value, 0.05)
	if model.Parent and math.abs(model:GetScale() - scale) > 0.004 then
		model:ScaleTo(scale)
	end
end

local function authoredBurst(source, cframe, scale, keepRotation)
	local effect = spawnAsset(source, cframe, scale, keepRotation)
	if not effect then return nil end
	local longest = 0.5
	local decals = {}
	for _, item in ipairs(effect:GetDescendants()) do
		if (item:IsA("Decal") or item:IsA("Texture")) and item.Transparency < 1 then
			table.insert(decals, item)
		elseif item:IsA("ParticleEmitter") then
			local delay = item:GetAttribute("EmitDelay")
			delay = type(delay) == "number" and math.max(delay, 0) or 0
			local count = item:GetAttribute("EmitCount")
			if type(count) ~= "number" or count <= 0 then
				count = math.clamp(math.floor(item.Rate * 0.25 + 0.5), 1, 24)
			end
			longest = math.max(longest, delay + item.Lifetime.Max / math.max(item.TimeScale, 0.05))
			task.delay(0.05 + delay, function()
				if item.Parent then
					item:Emit(count)
				end
			end)
		elseif item:IsA("Beam") then
			item.Enabled = true
		end
	end
	task.delay(0.05, function()
		if effect.Parent then
			flashLights(effect, 0.3)
		end
	end)
	task.delay(0.3, function()
		if effect.Parent then
			for _, item in ipairs(effect:GetDescendants()) do
				if item:IsA("Beam") then
					item.Enabled = false
				end
			end
		end
	end)
	if #decals > 0 then
		local fadeTime = math.min(0.6, longest * 0.5)
		task.delay(math.max(0.1, 0.05 + longest - fadeTime), function()
			if not effect.Parent then return end
			local info = TweenInfo.new(fadeTime, Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
			for _, decal in ipairs(decals) do
				if decal.Parent then
					TweenService:Create(decal, info, {Transparency = 1}):Play()
				end
			end
		end)
	end
	Debris:AddItem(effect, 0.05 + longest + 0.5)
	return effect
end

local function takeVFX(data, vfx)
	local index = vfx and table.find(data.extraVFX, vfx)
	if index then
		table.remove(data.extraVFX, index)
	end
	return vfx
end

local function cloneWelded(prefab, limb, parent, offset)
	if not prefab or not limb then return nil end
	local clone = prefab:Clone()
	if not clone:IsA("BasePart") then
		clone:Destroy()
		return nil
	end
	prepPart(clone)
	clone.Anchored = false
	clone.CFrame = limb.CFrame * (offset or CFrame.identity) * prefab.CFrame.Rotation
	clone.Parent = parent
	CollectionService:AddTag(clone, "RockModuleIgnore")
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = limb
	weld.Part1 = clone
	weld.Parent = clone
	return clone
end

local function playSound(soundId, position, volume)
	local holder = Instance.new("Part")
	holder.Name = "WonderWomanSound"
	holder.Size = Vector3.one
	holder.Transparency = 1
	holder.Anchored = true
	prepPart(holder)
	holder.Position = position
	holder.Parent = effectsFolder
	local sound = Instance.new("Sound")
	sound.SoundId = soundId
	sound.Volume = volume or 1
	sound.RollOffMaxDistance = 220
	sound.RollOffMode = Enum.RollOffMode.InverseTapered
	sound.Parent = holder
	sound:Play()
	Debris:AddItem(holder, 8)
	return holder
end

local function spawnDebris(position, totalRocks, minSize, maxSize)
	if not CraterModule or typeof(CraterModule.Explosion) ~= "function" then return end
	task.spawn(function()
		pcall(function()
			CraterModule.Explosion(CFrame.new(position), totalRocks, minSize, maxSize, false)
		end)
	end)
end

local function spawnCrater(position, radius, minRocks, maxRocks)
	if not CraterModule or typeof(CraterModule.Crater) ~= "function" then return end
	task.spawn(function()
		pcall(function()
			CraterModule.Crater(CFrame.new(position + UP * 0.1), radius, minRocks, maxRocks, false)
		end)
	end)
end

local function stomp(position, diameter)
	return authoredBurst(library:FindFirstChild("LeapImpact"), CFrame.new(position + UP * 0.2), diameter / STOMP_BASE, true)
end

local function applyRagdoll(character, duration, data)
	if not isCharacterValid(character) then return end
	if not CombatRules.canControl(character, data and data.targetLockId) then return end
	local flag = character:FindFirstChild("Ragdoll")
	if not flag then
		flag = Instance.new("BoolValue")
		flag.Name = "Ragdoll"
		flag.Parent = character
	end
	local currentId = "Ragdoll_" .. tostring(math.random())
	character:SetAttribute("CurrentRagdollId", currentId)
	flag.Value = true
	task.delay(duration, function()
		if character.Parent and character:GetAttribute("CurrentRagdollId") == currentId then
			local hum = character:FindFirstChildOfClass("Humanoid")
			if hum and hum.Health > 0 then
				flag.Value = false
				character:SetAttribute("CurrentRagdollId", nil)
			end
		end
	end)
end

local function dealDamage(caster, target, amount, options)
	local hum = target and target:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then return 0 end
	local dealt = coinDamage:Invoke(caster, hum, amount) or 0
	if dealt <= 0 then return 0 end
	if not (options and options.silent) then
		shakeCharacter(target, math.clamp(amount / 9, 0.8, 4), 10, 0.03, 0.3)
		applyTargetScreenEffect(target, options and options.screen or math.clamp(0.25 + amount / 60, 0.3, 0.8), options and options.color or AMAZON_GOLD)
	end
	return dealt
end

local lampEffects = shared.WitchLampEffects or {}
shared.WitchLampEffects = lampEffects
local LAMP_FLICKER = {{0.12, 0.12}, {0.85, 0.08}, {0, 0.16}, {0.7, 0.1}, {0.2, 0.18}, {1, 0.2}, {0.35, 0.09}, {0.9, 0.13}}

local function restoreLamp(lamp, state)
	if state.connection then
		state.connection:Disconnect()
		state.connection = nil
	end
	if lampEffects[lamp] ~= state then return end
	for _, saved in ipairs(state.saved) do
		if saved.object.Parent then
			saved.object.Enabled = saved.enabled
			if saved.brightness ~= nil then
				saved.object.Brightness = saved.brightness
			end
		end
	end
	lampEffects[lamp] = nil
end

local function claimLamp(lamp)
	local state = lampEffects[lamp]
	if state then return state end
	state = {saved = {}, owners = {}, step = 0, nextFlip = 0}
	for _, item in ipairs(lamp:GetDescendants()) do
		if item:IsA("Light") then
			table.insert(state.saved, {object = item, enabled = item.Enabled, brightness = item.Brightness})
		elseif item:IsA("Beam") then
			table.insert(state.saved, {object = item, enabled = item.Enabled})
		end
	end
	lampEffects[lamp] = state
	state.connection = RunService.Heartbeat:Connect(function()
		if not lamp.Parent or os.clock() >= (state.expiresAt or 0) then
			restoreLamp(lamp, state)
			return
		end
		for owner in pairs(state.owners) do
			if owner.stopped or not owner.character or not owner.character.Parent then
				state.owners[owner] = nil
			end
		end
		if not next(state.owners) then
			restoreLamp(lamp, state)
			return
		end
		local now = os.clock()
		if now < state.nextFlip then return end
		state.step = state.step % #LAMP_FLICKER + 1
		local step = LAMP_FLICKER[state.step]
		state.nextFlip = now + step[2]
		for _, saved in ipairs(state.saved) do
			if saved.object.Parent then
				saved.object.Enabled = saved.enabled and step[1] > 0.1
				if saved.brightness ~= nil then
					saved.object.Brightness = saved.brightness * step[1]
				end
			end
		end
	end)
	return state
end

local function shatterLamp(lamp, state)
	local now = os.clock()
	if now - (state.lastWonderWomanBurstAt or -math.huge) < 1 then return end
	state.lastWonderWomanBurstAt = now
	local shatter = lamp:FindFirstChild("GlassShatter")
	if not shatter then return end
	for _, item in ipairs(shatter:GetDescendants()) do
		if item:IsA("ParticleEmitter") then
			local count = item:GetAttribute("EmitCount")
			item:Emit(type(count) == "number" and count or 5)
		end
	end
	local glass = shatter:FindFirstChild("glass_sheet_break3", true)
	if glass and glass:IsA("Sound") then
		glass:Play()
	end
end

local function disturbLamps(owner, point, radius, hold, shatter)
	if not owner or owner.stopped then return end
	local interactables = workspace:FindFirstChild("Interactables")
	local lamps = interactables and interactables:FindFirstChild("StreetLights")
	if not lamps then return end
	local now = os.clock()
	for _, lamp in ipairs(lamps:GetChildren()) do
		local head = lamp:FindFirstChild("Part", true)
		if head and head:IsA("BasePart") then
			local delta = head.Position - point
			if Vector3.new(delta.X, 0, delta.Z).Magnitude <= radius then
				local state = claimLamp(lamp)
				state.expiresAt = math.max(state.expiresAt or 0, now + hold)
				state.owners[owner] = true
				owner.lamps[lamp] = true
				if shatter then
					shatterLamp(lamp, state)
				end
			end
		end
	end
end

local function releaseLamps(owner)
	if not owner then return end
	owner.stopped = true
	for lamp in pairs(owner.lamps) do
		owner.lamps[lamp] = nil
		local state = lampEffects[lamp]
		if state and state.owners[owner] then
			state.owners[owner] = nil
			if not next(state.owners) then
				restoreLamp(lamp, state)
			end
		end
	end
end

local function lampPulse(data, point, radius, hold, shatter)
	if data.stopped then return end
	local echo = {character = data.casterChar, stopped = false, lamps = {}}
	table.insert(data.lampEchoes, echo)
	disturbLamps(echo, point, radius, hold, shatter)
	task.delay(hold, releaseLamps, echo)
end

local function isLive(data)
	return data ~= nil and not data.stopped and isCharacterValid(data.casterChar)
end

local function waitFor(data, duration, step)
	local started = os.clock()
	local last = started
	while true do
		local now = os.clock()
		local elapsed = math.min(now - started, duration)
		if step and step(elapsed, now - last) == true then
			break
		end
		last = now
		if elapsed >= duration then
			break
		end
		RunService.Heartbeat:Wait()
		if not isLive(data) then
			return false
		end
	end
	return isLive(data)
end

local function castWindow(data, duration, step)
	local ok = waitFor(data, duration, step)
	local casterChar = data.casterChar
	if ok and casterChar and casterChar.Parent and casterChar:GetAttribute("AbilityLockId") == data.casterLockId then
		data.committed = true
		if not data.armorPending then
			CombatRules.grantArmor(casterChar, data.casterLockId, MAX_ABILITY_LIFETIME)
		end
	end
	return ok
end

local function armorOnLanding(data)
	if not data.armorPending then return end
	data.armorPending = false
	local casterChar = data.casterChar
	if data.committed and casterChar and casterChar.Parent and casterChar:GetAttribute("AbilityLockId") == data.casterLockId then
		CombatRules.grantArmor(casterChar, data.casterLockId, MAX_ABILITY_LIFETIME)
	end
end

local function rootCaster(data, factor, allowRotate)
	local casterChar = data.casterChar
	if not casterChar or not casterChar.Parent then return end
	if data.committed and not data.unstoppable then
		if factor >= 1 then
			CombatRules.releaseArmor(casterChar, data.casterLockId)
		elseif not data.armorPending and casterChar:GetAttribute("AbilityLockId") == data.casterLockId then
			CombatRules.grantArmor(casterChar, data.casterLockId, MAX_ABILITY_LIFETIME)
		end
	end
	MoveLock.apply(casterChar, data.casterLockId, {
		factor = factor,
		allowJump = factor >= 1,
		allowRotate = allowRotate == true,
		duration = MAX_ABILITY_LIFETIME,
	})
end

local function playAnim(data, character, animationId, fadeTime, speed)
	local track = AnimationManager:PlayAnimation(character, animationId, fadeTime or 0.1, 1, speed or 1)
	if track then
		table.insert(data.animTracks, track)
	end
	return track
end

local function attachHandGlows(data, character, limbNames)
	local prefab = library:FindFirstChild("BraceletGlow")
	if not prefab then return end
	for _, limbName in ipairs(limbNames) do
		local limb = character:FindFirstChild(limbName)
		if limb and limb:IsA("BasePart") then
			local glow = cloneWelded(prefab, limb, character)
			if glow then
				enableAll(glow)
				table.insert(data.handGlows, glow)
			end
		end
	end
end

local function dropHandGlows(data)
	for _, glow in ipairs(data.handGlows) do
		gracefullyCleanupVFX(glow)
	end
	table.clear(data.handGlows)
end

local function claimTarget(data, targetChar)
	if not targetChar or not targetChar.Parent then return end
	armorOnLanding(data)
	if CombatRules.isRagdolled(targetChar) then
		targetChar:SetAttribute("CurrentRagdollId", nil)
		setCharacterFlag(targetChar, "Ragdoll", false)
	end
	captureBaseStats(targetChar)
	targetChar:SetAttribute("TargetLockId", data.targetLockId)
	setCharacterFlag(targetChar, "BeingAttacked", true)
	MoveLock.apply(targetChar, data.targetLockId, {factor = 0, allowJump = false, allowRotate = false, duration = MAX_ABILITY_LIFETIME})
	table.insert(data.targets, {char = targetChar})
end

local function createHold(target)
	local root = target:FindFirstChild("HumanoidRootPart")
	local hum = target:FindFirstChildOfClass("Humanoid")
	if not (root and hum) then return nil end
	local attachment = Instance.new("Attachment")
	attachment.Name = "WonderWomanHold"
	attachment.Parent = root
	local align = Instance.new("AlignPosition")
	align.Name = "WonderWomanHoldPosition"
	align.Mode = Enum.PositionAlignmentMode.OneAttachment
	align.Attachment0 = attachment
	align.MaxForce = 1e6
	align.MaxVelocity = 220
	align.Responsiveness = 120
	align.ApplyAtCenterOfMass = true
	align.Position = root.Position
	align.Parent = root
	local orientation = Instance.new("AlignOrientation")
	orientation.Name = "WonderWomanHoldOrientation"
	orientation.Mode = Enum.OrientationAlignmentMode.OneAttachment
	orientation.Attachment0 = attachment
	orientation.MaxTorque = 1e6
	orientation.Responsiveness = 60
	orientation.CFrame = CFrame.lookAt(Vector3.zero, flatDirection(Vector3.zero, root.CFrame.LookVector, root.CFrame.LookVector))
	orientation.Parent = root
	root.AssemblyLinearVelocity = Vector3.zero
	root.AssemblyAngularVelocity = Vector3.zero
	local owner = Players:GetPlayerFromCharacter(target)
	pcall(function()
		root:SetNetworkOwner(nil)
	end)
	hum.PlatformStand = true
	local hold = {root = root, align = align, orientation = orientation, released = false}
	function hold.release(velocity)
		if hold.released then return end
		hold.released = true
		align:Destroy()
		orientation:Destroy()
		attachment:Destroy()
		if root.Parent then
			root.AssemblyAngularVelocity = Vector3.zero
			root.AssemblyLinearVelocity = velocity or Vector3.zero
			if hum.Parent and hum.Health > 0 and not flagOn(target, "Ragdoll") then
				hum.PlatformStand = false
			end
			pcall(function()
				if owner and owner.Parent then
					root:SetNetworkOwner(owner)
				else
					root:SetNetworkOwnershipAuto()
				end
			end)
		end
	end
	return hold
end

local function createAnchorHold(target)
	local root = target:FindFirstChild("HumanoidRootPart")
	local hum = target:FindFirstChildOfClass("Humanoid")
	if not (root and hum) then return nil end
	local owner = Players:GetPlayerFromCharacter(target)
	root.AssemblyLinearVelocity = Vector3.zero
	root.AssemblyAngularVelocity = Vector3.zero
	root.Anchored = true
	hum.PlatformStand = true
	local hold = {root = root, released = false}
	function hold.place(cframe)
		if hold.released or not root.Parent then return end
		root.CFrame = cframe
	end
	function hold.release(velocity)
		if hold.released then return end
		hold.released = true
		if not root.Parent then return end
		root.Anchored = false
		root.AssemblyAngularVelocity = Vector3.zero
		root.AssemblyLinearVelocity = velocity or Vector3.zero
		if hum.Parent and hum.Health > 0 and not flagOn(target, "Ragdoll") then
			hum.PlatformStand = false
		end
		pcall(function()
			if owner and owner.Parent then
				root:SetNetworkOwner(owner)
			else
				root:SetNetworkOwnershipAuto()
			end
		end)
	end
	return hold
end

local function applyTruth(data, target)
	truthCounter += 1
	local id = "WonderWomanTruth_" .. truthCounter
	target:SetAttribute("WonderWomanTruthId", id)
	target:SetAttribute("Silenced", true)
	local released = false
	local function release()
		if released then return end
		released = true
		if target.Parent and target:GetAttribute("WonderWomanTruthId") == id then
			target:SetAttribute("WonderWomanTruthId", nil)
			if not target:GetAttribute("EnchantressPossessedBy") then
				target:SetAttribute("Silenced", nil)
			end
		end
	end
	table.insert(data.cleanups, release)
	return release
end

local function watchTarget(data, target, onLost)
	local list = {}
	local function add(connection)
		table.insert(list, connection)
		table.insert(data.connections, connection)
	end
	local hum = target:FindFirstChildOfClass("Humanoid")
	if hum then
		add(hum.Died:Connect(onLost))
	end
	add(target.AncestryChanged:Connect(function()
		if not target:IsDescendantOf(workspace) then onLost() end
	end))
	local targetPlayer = Players:GetPlayerFromCharacter(target)
	if targetPlayer then
		add(targetPlayer.CharacterRemoving:Connect(function(removing)
			if removing == target then onLost() end
		end))
	end
	return list
end

local function unwatch(list)
	for _, connection in ipairs(list) do
		connection:Disconnect()
	end
	table.clear(list)
end

local function setFacing(data, character, point)
	character:SetAttribute("FlightFacingOwner", data.casterLockId)
	character:SetAttribute("FlightFacingPoint", point)
end

local function clearFacing(data, character)
	if character.Parent and character:GetAttribute("FlightFacingOwner") == data.casterLockId then
		character:SetAttribute("FlightFacingPoint", nil)
		character:SetAttribute("FlightFacingOwner", nil)
	end
end

local function quadBezier(p0, p1, p2, t)
	local u = 1 - t
	return p0 * (u * u) + p1 * (2 * u * t) + p2 * (t * t)
end

local function segmentDistance(point, a, b)
	local d = b - a
	local lengthSquared = d:Dot(d)
	if lengthSquared < 1e-6 then
		return (point - a).Magnitude
	end
	local t = math.clamp((point - a):Dot(d) / lengthSquared, 0, 1)
	return (point - (a + d * t)).Magnitude
end

local function charactersInArea(casterChar, center, radius, claiming)
	local list = {}
	for _, character in ipairs(CharacterIndex.Get()) do
		if character ~= casterChar then
			local root = character:FindFirstChild("HumanoidRootPart")
			if root and isInsideArea(root.Position, center, radius) and (if claiming then canBeGrabbed(character) else canBeHit(character)) then
				table.insert(list, character)
			end
		end
	end
	return list
end

local function lineClear(casterChar, target, range)
	local root = casterChar:FindFirstChild("HumanoidRootPart")
	local targetRoot = target:FindFirstChild("HumanoidRootPart")
	if not root or not targetRoot then return false end
	local delta = targetRoot.Position - root.Position
	if Vector3.new(delta.X, 0, delta.Z).Magnitude > range then return false end
	local ignored = {casterChar, target, effectsFolder}
	for _, tagged in ipairs(CollectionService:GetTagged("RockModuleIgnore")) do
		table.insert(ignored, tagged)
	end
	for _, child in ipairs(workspace:GetChildren()) do
		if child:FindFirstChildOfClass("Humanoid") then
			table.insert(ignored, child)
		end
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignored
	local origin = root.Position + UP * 1.5
	return workspace:Raycast(origin, (targetRoot.Position + UP * 1.5) - origin, params) == nil
end

local function ropeFrame(position, axis)
	local x = axis.Magnitude > 1e-4 and axis.Unit or Vector3.xAxis
	local reference = math.abs(x.Y) > 0.9 and Vector3.zAxis or UP
	local y = (reference - x * reference:Dot(x)).Unit
	return CFrame.fromMatrix(position, x, y)
end

local function handPoint(character)
	local hand = character:FindFirstChild("RightHand")
	if hand and hand:IsA("BasePart") then
		local grip = hand:FindFirstChild("RightGripAttachment")
		if grip and grip:IsA("Attachment") then
			return grip.WorldPosition
		end
		return hand.Position
	end
	local root = character:FindFirstChild("HumanoidRootPart")
	if root and root:IsA("BasePart") then
		return root.Position + root.CFrame.RightVector * 1.2 + UP * 0.4
	end
	return nil
end

local function createRope(data)
	local character = data.casterChar
	local hand = character:FindFirstChild("RightHand")
	local origin = handPoint(character)
	if not (origin and hand and hand:IsA("BasePart")) then return nil end

	local holder = Instance.new("Model")
	holder.Name = "LassoOfTruth"
	local casterValue = Instance.new("ObjectValue")
	casterValue.Name = "Caster"
	casterValue.Value = character
	casterValue.Parent = holder
	local hostValue = Instance.new("ObjectValue")
	hostValue.Name = "LoopHost"
	hostValue.Parent = holder
	holder:SetAttribute("Width", 0)
	holder:SetAttribute("Length", 0)

	local lineCount, loopCount = ROPE_LINE_NODES, ROPE_LOOP_NODES
	local points = table.create(lineCount, origin)
	local previous = table.create(lineCount, origin)
	local loopPoints = table.create(loopCount, origin)

	CollectionService:AddTag(holder, "RockModuleIgnore")
	CollectionService:AddTag(holder, "WonderWomanLasso")
	holder.Parent = effectsFolder

	local groundCast = groundParams(character)
	local rope = {
		holder = holder,
		length = 0,
		slack = 1,
		autoLength = false,
		tipGoal = nil,
		tipWorld = false,
		tipStiffness = 0,
		loop = nil,
		loopHost = nil,
		taut = false,
		widthScale = 0,
		disposed = false,
	}
	local connection

	local function currentLoopHost()
		local host = rope.loopHost
		if typeof(host) == "Instance" and host:IsA("BasePart") and host:IsDescendantOf(workspace) then
			return host
		end
		return nil
	end

	function rope.handPosition()
		return handPoint(character) or points[1]
	end

	function rope.tip()
		return points[lineCount]
	end

	function rope.knot()
		if rope.loop then
			return loopPoints[1]
		end
		return points[lineCount]
	end

	function rope.setWidth(scale)
		scale = math.max(scale, 0)
		if rope.disposed or math.abs(scale - rope.widthScale) < 0.005 then return end
		rope.widthScale = scale
	end

	local function buildLoop(handPos)
		local loop = rope.loop
		local normal = (loop.normal and loop.normal.Magnitude > 1e-4) and loop.normal.Unit or UP
		local toward = handPos - loop.center
		local u = toward - normal * toward:Dot(normal)
		if u.Magnitude < 1e-3 then
			u = normal:Cross(math.abs(normal.Y) > 0.9 and Vector3.xAxis or UP)
		end
		u = u.Unit
		local v = normal:Cross(u)
		local phase = loop.phase or 0
		local stepAngle = (2 * math.pi) / loopCount
		for j = 1, loopCount do
			local angle = phase + (j - 1) * stepAngle
			local point = loop.center + (u * math.cos(angle) + v * math.sin(angle)) * loop.radius
			if loop.ground then
				local hit = workspace:Raycast(point + UP * 5, Vector3.new(0, -12, 0), groundCast)
				if hit then
					point = Vector3.new(point.X, hit.Position.Y + 0.3, point.Z)
				end
			end
			loopPoints[j] = point
		end
	end

	local function publish()
		local root = character:FindFirstChild("HumanoidRootPart")
		local rootFrame = root and root.CFrame or CFrame.new(points[1])
		local loop = rope.loop
		holder:SetAttribute("Width", math.floor(rope.widthScale * 1000 + 0.5) / 1000)
		holder:SetAttribute("Length", rope.length)
		holder:SetAttribute("Slack", rope.slack)
		holder:SetAttribute("AutoLength", rope.autoLength)
		holder:SetAttribute("Taut", rope.taut and loop ~= nil)
		holder:SetAttribute("TipSpace", rope.tipWorld and "World" or "Root")
		holder:SetAttribute("TipGoal", rope.tipGoal and (if rope.tipWorld then rope.tipGoal else rootFrame:PointToObjectSpace(rope.tipGoal)) or nil)
		holder:SetAttribute("TipStiffness", rope.tipStiffness == math.huge and -1 or rope.tipStiffness)
		holder:SetAttribute("LoopOn", loop ~= nil)
		if loop then
			local host = currentLoopHost()
			hostValue.Value = host
			local space = if host then "Host" elseif loop.world then "World" else "Root"
			local frame = if host then host.CFrame elseif loop.world then CFrame.identity else rootFrame
			holder:SetAttribute("LoopSpace", space)
			holder:SetAttribute("LoopCenter", frame:PointToObjectSpace(loop.center))
			holder:SetAttribute("LoopNormal", (loop.normal and loop.normal.Magnitude > 1e-4) and loop.normal.Unit or UP)
			holder:SetAttribute("LoopRadius", loop.radius)
			holder:SetAttribute("LoopPhase", loop.phase or 0)
			holder:SetAttribute("LoopGround", loop.ground == true)
		elseif hostValue.Value then
			hostValue.Value = nil
		end
	end

	local function step(dt)
		if rope.disposed then return end
		if not character.Parent or not hand.Parent then
			rope.dispose()
			return
		end
		dt = math.clamp(dt, 1 / 240, 1 / 30)
		local handPos = handPoint(character) or points[1]
		if rope.loop then
			buildLoop(handPos)
		end
		if rope.autoLength then
			local goal = rope.loop and loopPoints[1] or rope.tipGoal
			if goal then
				rope.length = (goal - handPos).Magnitude * rope.slack
			end
		end
		local rest = math.max(rope.length, 0.02) / (lineCount - 1)
		local gravity = ROPE_GRAVITY * (dt * dt)
		for i = 2, lineCount do
			local current = points[i]
			local velocity = (current - previous[i]) * ROPE_DAMPING
			if velocity.Magnitude > ROPE_MAX_STEP then
				velocity = velocity.Unit * ROPE_MAX_STEP
			end
			previous[i] = current
			points[i] = current + velocity + gravity
		end
		points[1] = handPos
		previous[1] = handPos
		local pinned = false
		if rope.loop then
			points[lineCount] = loopPoints[1]
			pinned = true
		elseif rope.tipGoal then
			if rope.tipStiffness == math.huge then
				points[lineCount] = rope.tipGoal
				pinned = true
			elseif rope.tipStiffness > 0 then
				points[lineCount] = points[lineCount]:Lerp(rope.tipGoal, 1 - math.exp(-rope.tipStiffness * dt))
			end
		end
		for _ = 1, ROPE_ITERATIONS do
			for i = 1, lineCount - 1 do
				local a, b = points[i], points[i + 1]
				local delta = b - a
				local distance = delta.Magnitude
				if distance > 1e-5 then
					local wa = i == 1 and 0 or 1
					local wb = (pinned and i + 1 == lineCount) and 0 or 1
					local total = wa + wb
					if total > 0 then
						local correction = delta * ((distance - rest) / (distance * total))
						if wa > 0 then
							points[i] = a + correction
						end
						if wb > 0 then
							points[i + 1] = b - correction
						end
					end
				end
			end
		end
		publish()
	end

	function rope.dispose()
		if rope.disposed then return end
		rope.disposed = true
		if connection then
			connection:Disconnect()
			connection = nil
		end
		if holder.Parent then
			holder:SetAttribute("Disposed", true)
			Debris:AddItem(holder, 0.6)
		end
	end

	connection = RunService.Heartbeat:Connect(step)
	table.insert(data.ropes, rope)
	return rope
end

local function retractRope(data, rope, duration)
	if not rope or rope.disposed then return end
	rope.autoLength = false
	rope.taut = false
	rope.loopHost = nil
	rope.tipWorld = false
	local fromLength = rope.length
	local fromWidth = rope.widthScale
	local loop = rope.loop
	local fromRadius = loop and loop.radius or 0
	local fromCenter = loop and loop.center or nil
	if loop then
		loop.ground = false
		loop.world = false
	else
		rope.tipGoal = nil
		rope.tipStiffness = 0
	end
	waitFor(data, duration, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / duration, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		local hand = rope.handPosition()
		if loop and fromCenter then
			loop.center = fromCenter:Lerp(hand, k)
			loop.radius = fromRadius * (1 - k) + 0.05
			rope.length = (loop.center - hand).Magnitude + loop.radius
		else
			rope.length = fromLength * (1 - k)
			if k > 0.25 then
				rope.tipGoal = hand
				rope.tipStiffness = 8 + 30 * k
			end
		end
		rope.setWidth(fromWidth * (1 - 0.6 * k))
		return nil
	end)
	rope.dispose()
end

local function createZeusBeam(scale)
	local model = spawnAsset(library:FindFirstChild("ZeusBeam"), CFrame.identity, 1, false)
	if not model then return nil end
	local startPart = model:FindFirstChild("start")
	local startPart2 = model:FindFirstChild("start1")
	local endPart = model:FindFirstChild("end1")
	local middles = {model:FindFirstChild("middle"), model:FindFirstChild("middle1")}
	if not (startPart and endPart) then
		model:Destroy()
		return nil
	end
	local beams = {}
	for _, item in ipairs(model:GetDescendants()) do
		if item:IsA("Beam") then
			beams[item] = {item.Width0, item.Width1}
		end
	end
	local shot = {model = model, bound = false}
	function shot.width(k)
		local w = math.max(k, 0) * scale
		for beam, base in pairs(beams) do
			beam.Width0 = base[1] * w
			beam.Width1 = base[2] * w
		end
	end
	function shot.bind(startHost, startOffset, endHost, endOffset)
		if not (startHost and endHost and startHost.Parent and endHost.Parent) then return false end
		local function bindPart(part, host, offset)
			part.Anchored = false
			part.CFrame = host.CFrame * offset
			local weld = Instance.new("Weld")
			weld.Part0 = host
			weld.Part1 = part
			weld.C0 = offset
			weld.Parent = part
		end
		bindPart(startPart, startHost, startOffset)
		if startPart2 then
			bindPart(startPart2, startHost, startOffset)
		end
		bindPart(endPart, endHost, endOffset)
		shot.bound = true
		return true
	end
	function shot.place(from, to)
		if shot.bound then
			from, to = startPart.Position, endPart.Position
		end
		local delta = to - from
		if delta.Magnitude < 0.05 then
			delta = -UP * 0.05
		end
		local direction = delta.Unit
		if not shot.bound then
			local look = CFrame.lookAt(from, from + direction)
			startPart.CFrame = look
			if startPart2 then
				startPart2.CFrame = look
			end
			endPart.CFrame = CFrame.lookAt(to, to + direction)
		end
		local frame = ropeFrame(from + delta * 0.5, direction)
		for _, middle in ipairs(middles) do
			if middle and middle:IsA("BasePart") then
				middle.Size = Vector3.new(math.max(delta.Magnitude, 0.5), middle.Size.Y, middle.Size.Z)
				middle.CFrame = frame
			end
		end
	end
	function shot.collapse(duration)
		local began = os.clock()
		local connection
		connection = RunService.Heartbeat:Connect(function()
			local alpha = (os.clock() - began) / duration
			if alpha >= 1 or not model.Parent then
				connection:Disconnect()
				gracefullyCleanupVFX(model)
				return
			end
			shot.width(1 - alpha)
		end)
	end
	shot.width(0)
	enableAll(model)
	return shot
end

local function lockBody(character)
	local root = character:FindFirstChild("HumanoidRootPart")
	local saved = {}
	for _, part in ipairs(character:GetDescendants()) do
		if part:IsA("BasePart") then
			saved[part] = {part.CanCollide, part.CanTouch}
			part.CanCollide = false
			part.CanTouch = false
		end
	end
	if root then
		root.AssemblyLinearVelocity = Vector3.zero
		root.AssemblyAngularVelocity = Vector3.zero
		root.Anchored = true
	end
	local released = false
	return function()
		if released then return end
		released = true
		for part, state in pairs(saved) do
			if part.Parent then
				part.CanCollide, part.CanTouch = state[1], state[2]
			end
		end
		if root and root.Parent then
			root.Anchored = false
			root.AssemblyLinearVelocity = Vector3.zero
			root.AssemblyAngularVelocity = Vector3.zero
		end
	end
end

local function attachModel(model, part, offset)
	local primary = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart", true)
	if not (primary and part and part:IsA("BasePart")) then return nil end
	for _, item in ipairs(model:GetDescendants()) do
		if item:IsA("BasePart") then
			item.Anchored = false
			item.Massless = true
			if item ~= primary then
				local constraint = Instance.new("WeldConstraint")
				constraint.Part0 = primary
				constraint.Part1 = item
				constraint.Parent = item
			end
		end
	end
	primary.CFrame = part.CFrame * offset
	local weld = Instance.new("Weld")
	weld.Part0 = part
	weld.Part1 = primary
	weld.C0 = offset
	weld.Parent = primary
	return weld
end

local function mountSword(data, character)
	local prefab = library:FindFirstChild("GodkillerSword")
	local hand = character:FindFirstChild("RightHand")
	if not (prefab and prefab:IsA("BasePart") and hand and hand:IsA("BasePart")) then return nil end
	local grip = hand:FindFirstChild("RightGripAttachment")
	local offset = (grip and grip:IsA("Attachment")) and grip.CFrame or CFrame.new(0, -0.15, 0) * CFrame.Angles(-math.pi / 2, 0, 0)
	local sword = prefab:Clone()
	for _, item in ipairs(all(sword)) do
		if item:IsA("BasePart") then
			prepPart(item)
			item.Anchored = false
		end
	end
	sword.CFrame = hand.CFrame * offset
	CollectionService:AddTag(sword, "RockModuleIgnore")
	sword.Parent = effectsFolder
	local weld = Instance.new("Weld")
	weld.Part0 = hand
	weld.Part1 = sword
	weld.C0 = offset
	weld.Parent = sword
	for _, item in ipairs(sword:GetDescendants()) do
		if item:IsA("Trail") then
			item.Enabled = true
		end
	end
	task.delay(0.05, function()
		if not sword.Parent then return end
		for _, item in ipairs(sword:GetDescendants()) do
			if item:IsA("ParticleEmitter") then
				local count = item:GetAttribute("EmitCount")
				item:Emit(type(count) == "number" and count > 0 and count or 2)
			end
		end
	end)
	table.insert(data.extraVFX, sword)
	return sword
end

local function mountWings(data, character, scale)
	local prefab = library:FindFirstChild("EagleWings")
	local torso = character:FindFirstChild("UpperTorso") or character:FindFirstChild("Torso")
	if not (prefab and torso and torso:IsA("BasePart")) then return nil end
	local model = prefab:Clone()
	local authored = {}
	for _, item in ipairs(model:GetDescendants()) do
		if item:IsA("BasePart") then
			prepPart(item)
			item.Anchored = false
		elseif item:IsA("Motor6D") and item.Part0 == nil then
			authored[item] = item.C0
		end
	end
	if next(authored) == nil then
		model:Destroy()
		return nil
	end
	model:ScaleTo(model:GetScale() * scale)
	model:PivotTo(torso.CFrame)
	local joints = {}
	for motor, c0 in pairs(authored) do
		motor.C0 = c0
		motor.Part0 = torso
		table.insert(joints, {motor = motor, open = c0, side = c0.Position.X >= 0 and 1 or -1})
	end
	CollectionService:AddTag(model, "RockModuleIgnore")
	model.Parent = effectsFolder
	table.insert(data.extraVFX, model)
	return {model = model, joints = joints}
end

local function slashFrame(point, approach, tilt)
	local forward = approach.Magnitude > 1e-3 and approach.Unit or Vector3.new(0, 0, -1)
	local normal = CFrame.fromAxisAngle(forward, tilt):VectorToWorldSpace(UP)
	local lateral = normal:Cross(forward)
	if lateral.Magnitude < 1e-3 then
		lateral = Vector3.xAxis
	end
	return CFrame.fromMatrix(point, lateral.Unit, normal.Unit)
end

local function animateSlash(effect, mesh, cframe, sweep, fromTransparency)
	for _, item in ipairs(effect:GetDescendants()) do
		if item:IsA("Trail") then
			item.Enabled = true
		end
	end
	task.delay(0.02, function()
		if not effect.Parent then return end
		for _, item in ipairs(effect:GetDescendants()) do
			if item:IsA("ParticleEmitter") then
				local count = item:GetAttribute("EmitCount")
				item:Emit(type(count) == "number" and count > 0 and count or 4)
			end
		end
	end)
	local baseSize = mesh.Size
	local began = os.clock()
	local duration = 0.24
	local connection
	connection = RunService.Heartbeat:Connect(function()
		if not effect.Parent or not mesh.Parent then
			connection:Disconnect()
			return
		end
		local alpha = math.clamp((os.clock() - began) / duration, 0, 1)
		local eased = TweenService:GetValue(alpha, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		mesh.CFrame = cframe * CFrame.Angles(0, sweep * eased, 0)
		mesh.Size = baseSize * (0.85 + 0.3 * eased)
		mesh.Transparency = fromTransparency + (1 - fromTransparency) * alpha ^ 1.6
		if alpha >= 1 then
			connection:Disconnect()
			gracefullyCleanupVFX(effect)
		end
	end)
end

local function slashArc(cframe, scale, sweep)
	local effect = spawnAsset(library:FindFirstChild("GodkillerSlash"), cframe, scale, false)
	if not effect then return nil end
	local mesh = effect.PrimaryPart
	if not mesh then
		gracefullyCleanupVFX(effect)
		return nil
	end
	animateSlash(effect, mesh, cframe, sweep or 0.6, 0.1)
	return effect
end

local function cutMark(data, cframe, scale)
	local effect = spawnAsset(library:FindFirstChild("GodkillerSlash"), cframe, scale, false)
	if not effect then return nil end
	local mesh = effect.PrimaryPart
	if not mesh then
		gracefullyCleanupVFX(effect)
		return nil
	end
	mesh.Transparency = 1
	TweenService:Create(mesh, TweenInfo.new(0.08, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Transparency = 0.4}):Play()
	table.insert(data.extraVFX, effect)
	return {effect = effect, mesh = mesh, cframe = cframe}
end

local function releaseCut(data, mark, sweep)
	if not mark or not mark.effect.Parent or not mark.mesh.Parent then return end
	takeVFX(data, mark.effect)
	animateSlash(mark.effect, mark.mesh, mark.cframe, sweep, 0.05)
end

local function scaleCooldown(caster, abilityName, scale)
	local cfg = ABILITY_CONFIG[abilityName]
	if not cfg or not cfg.cooldown or caster:GetAttribute("CooldownsDisabled") then return end
	cooldowns[caster.UserId] = cooldowns[caster.UserId] or {}
	cooldowns[caster.UserId][abilityName] = os.clock() + cfg.cooldown * scale
	remoteEvent:FireClient(caster, "CooldownScale", {ability = abilityName, scale = scale})
end

local function stopAbility(casterId, instanceKey, isClean)
	local perUser = activeAbilities[casterId]
	local data = perUser and perUser[instanceKey]
	if not data then return end
	CombatRules.releasePriority(data.casterLockId)
	local abilityName = data.abilityName
	data.stopped = true
	perUser[instanceKey] = nil
	if next(perUser) == nil then
		activeAbilities[casterId] = nil
	end

	if data.onStop then
		local hook = data.onStop
		data.onStop = nil
		local ok, err = pcall(hook, isClean)
		if not ok then
			warn(string.format("[WonderWoman] %s cleanup failed: %s", abilityName, tostring(err)))
		end
	end

	if data.mainThread and data.mainThread ~= coroutine.running() then
		pcall(task.cancel, data.mainThread)
	end
	for _, conn in ipairs(data.connections) do
		if conn.Connected then
			conn:Disconnect()
		end
	end
	table.clear(data.connections)
	for _, track in ipairs(data.animTracks) do
		pcall(function()
			track:Stop(0.2)
		end)
	end
	table.clear(data.animTracks)

	for _, hold in ipairs(data.holds) do
		pcall(hold.release, Vector3.zero)
	end
	table.clear(data.holds)
	for _, cleanup in ipairs(data.cleanups) do
		local ok, err = pcall(cleanup)
		if not ok then
			warn(string.format("[WonderWoman] %s release failed: %s", abilityName, tostring(err)))
		end
	end
	table.clear(data.cleanups)
	for _, rope in ipairs(data.ropes) do
		rope.dispose()
	end
	table.clear(data.ropes)

	local casterChar = data.casterChar
	if casterChar then
		MoveLock.release(casterChar, data.casterLockId)
		CombatRules.releaseArmor(casterChar, data.casterLockId)
		if casterChar.Parent and casterChar:GetAttribute("AbilityLockId") == data.casterLockId then
			casterChar:SetAttribute("AbilityLockId", nil)
			setCharacterFlag(casterChar, "Invulnerable", false)
			setCharacterFlag(casterChar, "AbilityActive", false)
			local hum = casterChar:FindFirstChildOfClass("Humanoid")
			if hum and hum.Health > 0 then
				restoreStats(casterChar)
			end
		end
	end

	for _, targetData in ipairs(data.targets) do
		local target = targetData.char
		if target then
			MoveLock.release(target, data.targetLockId)
			if target.Parent and target:GetAttribute("TargetLockId") == data.targetLockId then
				target:SetAttribute("TargetLockId", nil)
				setCharacterFlag(target, "BeingAttacked", false)
				local hum = target:FindFirstChildOfClass("Humanoid")
				if hum and hum.Health > 0 then
					restoreStats(target)
				end
			end
		end
	end
	table.clear(data.targets)

	dropHandGlows(data)
	for _, vfx in ipairs(data.extraVFX) do
		gracefullyCleanupVFX(vfx)
	end
	table.clear(data.extraVFX)
	if not isClean then
		for _, echo in ipairs(data.lampEchoes) do
			releaseLamps(echo)
		end
	end
	table.clear(data.lampEchoes)

	if not isClean and cooldowns[casterId] then
		cooldowns[casterId][abilityName] = nil
	end

	local casterPlayer = Players:GetPlayerByUserId(casterId)
	if casterPlayer then
		remoteEvent:FireClient(casterPlayer, isClean and "CastFinished" or "ForceStop", abilityName)
	end
end

local abilityHandlers = {}
local validators = {}

local function groundTarget(casterChar, point, range)
	local root = casterChar:FindFirstChild("HumanoidRootPart")
	if not root then return nil end
	local flat = Vector3.new(point.X - root.Position.X, 0, point.Z - root.Position.Z)
	if flat.Magnitude > range then
		flat = flat.Unit * range
	end
	local probe = root.Position + flat
	local hit = workspace:Raycast(Vector3.new(probe.X, math.max(point.Y, root.Position.Y) + 100, probe.Z), Vector3.new(0, -220, 0), groundParams(casterChar))
	if not hit or hit.Normal.Y < 0.45 then return nil end
	return hit.Position
end

abilityHandlers.LassoLash = function(caster, data, aimPoint)
	local cfg = ABILITY_CONFIG.LassoLash
	local character = data.casterChar
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	if not character:GetAttribute("IsFlying") then stabilizeCharacter(character, aimPoint) end
	rootCaster(data, 0.45, true)
	attachHandGlows(data, character, {"RightHand"})
	-- ONE animation covers windup -> crack (HIT at frame 29) -> recoil
	playAnim(data, character, WW_ANIMS.LassoLash, 0.05, 1)
	playSound(SOUNDS.Ribbon, root.Position, 0.5)
	local rope = createRope(data)
	if not rope then return end
	local forward = flatDirection(root.Position, aimPoint, root.CFrame.LookVector)
	local right = forward:Cross(UP)
	rope.tipStiffness = 16
	if not castWindow(data, cfg.castTime, function(elapsed)
		local k = math.clamp(elapsed / cfg.castTime, 0, 1)
		local eased = TweenService:GetValue(k, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		local hand = rope.handPosition()
		rope.length = 1 + 5 * eased
		rope.setWidth(math.min(1, k * 2.5))
		rope.tipGoal = hand - forward * (1.5 + 3 * eased) + UP * (1.5 + 2.5 * eased) + right * 0.8
		return nil
	end) then return end

	local hand = rope.handPosition()
	local toAim = aimPoint - hand
	local flat = Vector3.new(toAim.X, 0, toAim.Z)
	local flatUnit = flat.Magnitude > 0.1 and flat.Unit or forward
	local pitch = math.clamp(math.atan2(toAim.Y, math.max(flat.Magnitude, 0.1)), -0.6, 0.6)
	local direction = flatUnit * math.cos(pitch) + UP * math.sin(pitch)
	local reach = math.clamp(toAim.Magnitude, cfg.minReach, cfg.range)
	local wall = workspace:Raycast(hand, direction * reach, groundParams(character))
	if wall then
		reach = math.max(cfg.minReach * 0.5, wall.Distance - 0.4)
	end
	local strikePoint = hand + direction * reach
	local from = rope.tip()
	local apex = hand + UP * (2.5 + reach * 0.22) + direction * (reach * 0.3)
	playSound(SOUNDS.Woosh, hand, 0.9)
	rope.tipWorld = true
	rope.tipStiffness = 55
	if not waitFor(data, cfg.crackTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.crackTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		rope.length = math.max(6, 6 + (reach * 1.03 - 6) * k)
		rope.tipGoal = quadBezier(from, apex, strikePoint, k)
		return nil
	end) then return end

	rope.tipGoal = strikePoint
	rope.tipStiffness = math.huge
	rope.length = reach
	authoredBurst(library:FindFirstChild("LashCrack"), CFrame.new(strikePoint), 0.7)
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(strikePoint), 0.45)
	playSound(SOUNDS.Impact, strikePoint, 0.95)
	shakeArea(strikePoint, 30, 1.6, 14, 0.02, 0.22)

	local handNow = rope.handPosition()
	local struck = {}
	for _, target in ipairs(CharacterIndex.Get()) do
		if target ~= character and canBeHit(target) then
			local targetRoot = target:FindFirstChild("HumanoidRootPart")
			if targetRoot then
				local tipDistance = (targetRoot.Position - strikePoint).Magnitude
				if tipDistance <= cfg.tipRadius or segmentDistance(targetRoot.Position, handNow, strikePoint) <= cfg.lineRadius then
					table.insert(struck, {target = target, root = targetRoot, tip = tipDistance <= cfg.tipRadius})
				end
			end
		end
	end
	for _, hit in ipairs(struck) do
		local amount = cfg.damage + (hit.tip and cfg.tipDamage or 0)
		if dealDamage(caster, hit.target, amount, {screen = hit.tip and 0.5 or 0.3}) > 0 and isCharacterValid(hit.target) then
			glowPulse(hit.target, 0.01, 0.05, 0.3)
			applyRagdoll(hit.target, cfg.ragdoll, data)
			local push = flatDirection(root.Position, hit.root.Position, forward)
			if hit.tip then
				authoredBurst(library:FindFirstChild("LashHit"), CFrame.new(hit.root.Position), 0.8)
				launch(hit.root, push * cfg.tipKnockback + UP * cfg.tipLift, data)
			else
				launch(hit.root, push * cfg.knockback + UP * 3, data)
			end
		end
	end

	rope.tipGoal = nil
	rope.tipWorld = false
	rope.tipStiffness = 0
	rootCaster(data, 1, true)
	playSound(SOUNDS.Woosh, strikePoint, 0.45)
	local recoilFrom = rope.length
	waitFor(data, cfg.recoilTime, function(elapsed)
		local k = math.clamp(elapsed / cfg.recoilTime, 0, 1)
		local eased = TweenService:GetValue(k, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		rope.length = recoilFrom * (1 - eased)
		rope.setWidth(1 - eased * 0.5)
		if k > 0.25 then
			rope.tipGoal = rope.handPosition()
			rope.tipStiffness = 14 * k
		end
		return nil
	end)
	rope.dispose()
end

validators.LassoOfTruth = function(_, casterChar, target)
	if lineClear(casterChar, target, ABILITY_CONFIG.LassoOfTruth.range + RANGE_TOLERANCE) then return target end
	return nil
end

abilityHandlers.LassoOfTruth = function(caster, data, target)
	local cfg = ABILITY_CONFIG.LassoOfTruth
	local character = data.casterChar
	local root = character:FindFirstChild("HumanoidRootPart")
	local targetRoot = target:FindFirstChild("HumanoidRootPart")
	local targetHum = target:FindFirstChildOfClass("Humanoid")
	if not (root and targetRoot and targetHum) then return end
	local function stop()
		stopAbility(caster.UserId, data.instanceKey, true)
	end
	local targetConnections = watchTarget(data, target, stop)
	local function torsoPoint()
		local torso = torsoOf(target)
		return torso and torso.Position or targetRoot.Position
	end
	local function face()
		if targetRoot.Parent then
			setFacing(data, character, targetRoot.Position)
		end
	end
	local function interrupted()
		return not isLive(data) or caster.Character ~= character or CombatRules.interrupts(character)
			or not isCharacterValid(target) or not target:IsDescendantOf(workspace)
			or flagOn(target, "Invulnerable") or target:FindFirstChildOfClass("ForceField") ~= nil
	end
	local function held()
		return isCharacterValid(target) and target:GetAttribute("TargetLockId") == data.targetLockId
			and not flagOn(target, "Invulnerable") and target:FindFirstChildOfClass("ForceField") == nil
	end
	data.onStop = function()
		clearFacing(data, character)
	end

	attachHandGlows(data, character, {"RightHand"})
	-- ONE animation covers spin -> throw -> haul/compel -> hurl (SLAM at frame 165) -> recover
	playAnim(data, character, WW_ANIMS.LassoOfTruth, 0.08, 1)
	playSound(SOUNDS.Ribbon, root.Position, 0.6)
	playSound(SOUNDS.Whisper, root.Position, 0.4)
	local rope = createRope(data)
	if not rope then return end
	rope.loop = {center = rope.handPosition() + UP * 1.3, normal = UP, radius = 0.7, phase = 0}
	rope.autoLength = true
	rope.slack = 1.1
	local spin = 0
	if not castWindow(data, cfg.castTime, function(elapsed, dt)
		if interrupted() then
			stop()
			return true
		end
		face()
		local k = math.clamp(elapsed / cfg.castTime, 0, 1)
		spin += dt * cfg.spinSpeed
		local hand = rope.handPosition()
		local orbit = Vector3.new(math.cos(spin), 0, math.sin(spin)) * (0.6 + 0.6 * k)
		rope.loop.center = hand + UP * (1.3 + 0.9 * k) + orbit
		rope.loop.radius = 0.7 + (cfg.loopRadius - 0.7) * k
		rope.loop.phase = spin * 0.5
		rope.setWidth(math.min(1, k * 2.2))
		return nil
	end) then return end
	if interrupted() or not canBeAffected(target) or not lineClear(character, target, cfg.range + RANGE_TOLERANCE) then
		data.fizzled = true
		retractRope(data, rope, 0.25)
		return
	end

	playSound(SOUNDS.Woosh, rope.handPosition(), 0.9)
	local from = rope.loop.center
	local openRadius = cfg.loopRadius + 0.5
	local distance = (torsoPoint() - from).Magnitude
	local travel = cfg.throwTime -- fixed so the single animation stays in sync
	local lift = UP * (2 + distance * 0.1)
	local phase0 = (spin * 0.5) % (2 * math.pi)
	rope.loop.world = true
	if not waitFor(data, travel, function(elapsed)
		if interrupted() then
			stop()
			return true
		end
		face()
		local k = TweenService:GetValue(math.clamp(elapsed / travel, 0, 1), Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
		local goal = torsoPoint() + UP * cfg.dropHeight
		rope.loop.center = quadBezier(from, (from + goal) * 0.5 + lift, goal, k)
		rope.loop.phase = phase0 + (2 * math.pi - phase0) * k
		rope.loop.radius = cfg.loopRadius + (openRadius - cfg.loopRadius) * k
		rope.slack = 1.12 - 0.08 * k
		return nil
	end) then return end
	if not canBeAffected(target) then
		data.fizzled = true
		retractRope(data, rope, 0.3)
		return
	end

	playSound(SOUNDS.Ribbon, torsoPoint(), 0.7)
	rope.loopHost = torsoOf(target)
	if not waitFor(data, cfg.cinchTime, function(elapsed)
		if interrupted() then
			stop()
			return true
		end
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.cinchTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		local torso = torsoPoint()
		rope.loop.center = (torso + UP * cfg.dropHeight):Lerp(torso, k)
		rope.loop.radius = openRadius + (cfg.bindRadius - openRadius) * k
		return nil
	end) then return end
	if not canBeAffected(target) then
		data.fizzled = true
		retractRope(data, rope, 0.3)
		return
	end

	claimTarget(data, target)
	local hold = createHold(target)
	if not hold then return end
	table.insert(data.holds, hold)
	local releaseTruth = applyTruth(data, target)
	local aura = spawnAsset(library:FindFirstChild("TruthAura"), CFrame.new(torsoPoint()), cfg.auraScale, false)
	local auraWeld
	if aura then
		enableAll(aura)
		table.insert(data.extraVFX, aura)
		local auraHost = torsoOf(target)
		auraWeld = auraHost and attachModel(aura, auraHost, CFrame.identity)
	end
	authoredBurst(library:FindFirstChild("LashHit"), CFrame.new(torsoPoint()), 0.9)
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(torsoPoint() + UP), 0.6)
	glowPulse(target, 0.02, cfg.reelTime + cfg.compelTime, 0.3)
	playSound(SOUNDS.Impact, torsoPoint(), 0.85)
	playSound(SOUNDS.Transform, torsoPoint(), 0.7)
	shakeCharacter(target, 2.2, 12, 0.02, 0.35)
	shakeCharacter(character, 1.1, 10, 0.02, 0.25)
	applyTargetScreenEffect(target, 0.8, TRUTH_GOLD)
	dealDamage(caster, target, cfg.tickDamage, {silent = true})
	local victimTrack = AnimationManager:PlayAnimation(target, WW_ANIMS.Victim, 0.1, 1, 0.8)
	if victimTrack then
		table.insert(data.animTracks, victimTrack)
	end
	rope.slack = 1
	rope.taut = true

	local function track()
		local torso = torsoPoint()
		rope.loop.center = torso
		rope.loop.radius = cfg.bindRadius
		rope.loop.phase = 0
		if auraWeld and auraWeld.Parent then
			auraWeld.C0 = CFrame.Angles(0, os.clock() * 2.2, 0)
		end
	end

	local reelFrom = targetRoot.Position
	local forward = flatDirection(root.Position, reelFrom, root.CFrame.LookVector)
	local targetStand = standHeight(target)
	local function frontOfCaster()
		local towardTarget = flatDirection(root.Position, targetRoot.Position, forward)
		local spot = root.Position + towardTarget * cfg.reelGap
		local floor = findFloor(spot + UP * 3, target)
		if floor then
			spot = Vector3.new(spot.X, math.max(spot.Y, floor.Y + targetStand), spot.Z)
		end
		return spot, towardTarget
	end
	playSound(SOUNDS.Woosh, reelFrom, 0.8)
	if not waitFor(data, cfg.reelTime, function(elapsed)
		if not held() then
			stop()
			return true
		end
		face()
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.reelTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		local spot, towardTarget = frontOfCaster()
		hold.align.Position = reelFrom:Lerp(spot, k) + UP * (math.sin(k * math.pi) * 2.2)
		hold.orientation.CFrame = CFrame.lookAt(Vector3.zero, -towardTarget)
		track()
		return nil
	end) or not held() then return end

	local nextTick = cfg.tickInterval
	if not waitFor(data, cfg.compelTime, function(elapsed)
		if not held() then
			stop()
			return true
		end
		face()
		local spot, towardTarget = frontOfCaster()
		hold.align.Position = spot + UP * (0.6 + math.sin(elapsed * 6) * 0.25)
		hold.orientation.CFrame = CFrame.lookAt(Vector3.zero, -towardTarget)
		track()
		rope.setWidth(1 + 0.3 * math.sin(elapsed * 18) ^ 2)
		if elapsed >= nextTick then
			nextTick += cfg.tickInterval
			if dealDamage(caster, target, cfg.tickDamage, {silent = true}) > 0 then
				authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(torsoPoint()), 0.35)
				shakeCharacter(target, 1, 12, 0.02, 0.15)
			end
		end
		return nil
	end) or not held() then return end
	rope.setWidth(1)

	playSound(SOUNDS.Woosh, targetRoot.Position, 1)
	playSound(SOUNDS.Swing, root.Position, 0.7)
	local start = targetRoot.Position
	forward = flatDirection(root.Position, start, forward)
	local behind = root.Position - forward * cfg.slamBack
	local slamFloor = findFloor(behind + UP * 4, target) or getGroundPosition(behind, target)
	local landing = slamFloor + UP * 1.2
	local apex = root.Position + UP * cfg.slamHeight - forward * 1.5
	local headroom = workspace:Raycast(root.Position, UP * (cfg.slamHeight + 3), groundParams(target))
	if headroom then
		apex = Vector3.new(apex.X, math.max(root.Position.Y + 4, headroom.Position.Y - 3), apex.Z)
	end
	if not waitFor(data, cfg.hurlTime, function(elapsed)
		if not held() then
			stop()
			return true
		end
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.hurlTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		hold.align.Position = quadBezier(start, apex, landing, k)
		hold.orientation.CFrame = CFrame.lookAt(Vector3.zero, -forward) * CFrame.Angles(-math.pi * k, 0, 0)
		track()
		return nil
	end) or not held() then return end

	unwatch(targetConnections)
	if victimTrack then
		pcall(function()
			victimTrack:Stop(0.05)
		end)
	end
	hold.release(Vector3.zero)
	releaseTruth()
	if aura then
		gracefullyCleanupVFX(takeVFX(data, aura))
	end
	stomp(slamFloor, cfg.craterRadius * 3)
	spawnCrater(slamFloor, cfg.craterRadius, 8, 12)
	spawnDebris(slamFloor + UP, 8, 0.4, 1)
	authoredBurst(library:FindFirstChild("LashHit"), CFrame.new(slamFloor + UP), 1)
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(slamFloor + UP * 1.5), 0.9)
	playSound(SOUNDS.Slam, slamFloor, 1)
	playSound(SOUNDS.RockBreak, slamFloor, 0.85)
	shakeArea(slamFloor, 55, 3.4, 11, 0.02, 0.45)
	if dealDamage(caster, target, cfg.slamDamage, {screen = 0.85, color = TRUTH_GOLD}) > 0 and isCharacterValid(target) then
		glowPulse(target, 0.01, 0.06, 0.35)
		applyRagdoll(target, cfg.ragdoll, data)
		launch(targetRoot, -forward * 6 + UP * cfg.bounce, data)
	end
	rope.loop.radius = cfg.bindRadius * 2
	retractRope(data, rope, 0.32)
end

validators.HestiasSnare = function(_, casterChar, point)
	return groundTarget(casterChar, point, ABILITY_CONFIG.HestiasSnare.range)
end

abilityHandlers.HestiasSnare = function(caster, data, center)
	local cfg = ABILITY_CONFIG.HestiasSnare
	local character = data.casterChar
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	attachHandGlows(data, character, {"RightHand"})
	-- ONE animation covers spin -> throw -> cinch -> lift -> slam (IMPACT at frame 143) -> reel in
	playAnim(data, character, WW_ANIMS.HestiasSnare, 0.08, 1)
	playSound(SOUNDS.Ribbon, root.Position, 0.65)
	playSound(SOUNDS.Whisper, center, 0.5)
	local rope = createRope(data)
	if not rope then return end
	rope.loop = {center = rope.handPosition() + UP * 1.3, normal = UP, radius = 0.8, phase = 0}
	rope.autoLength = true
	rope.slack = 1.1
	local spin = 0
	if not castWindow(data, cfg.castTime, function(elapsed, dt)
		local k = math.clamp(elapsed / cfg.castTime, 0, 1)
		spin += dt * cfg.spinSpeed
		local hand = rope.handPosition()
		local orbit = Vector3.new(math.cos(spin), 0, math.sin(spin)) * (0.7 + 0.8 * k)
		rope.loop.center = hand + UP * (1.4 + 1.1 * k) + orbit
		rope.loop.radius = 0.8 + (cfg.spinRadius - 0.8) * k
		rope.loop.phase = spin * 0.5
		rope.setWidth(math.min(1, k * 2))
		return nil
	end) then return end

	playSound(SOUNDS.Woosh, rope.handPosition(), 1)
	local from = rope.loop.center
	local air = center + UP * cfg.throwHeight
	local distance = (air - from).Magnitude
	local travel = cfg.throwTime -- fixed so the single animation stays in sync
	local control = (from + air) * 0.5 + UP * (3 + distance * 0.12)
	local phase0 = (spin * 0.5) % (2 * math.pi)
	rope.loop.world = true
	if not waitFor(data, travel, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / travel, 0, 1), Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
		rope.loop.center = quadBezier(from, control, air, k)
		rope.loop.radius = cfg.spinRadius + (cfg.radius - cfg.spinRadius) * k
		rope.loop.phase = phase0 + (2 * math.pi - phase0) * k
		return nil
	end) then return end

	rope.loop.ground = true
	if not waitFor(data, cfg.dropTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.dropTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		rope.loop.center = air:Lerp(center + UP * 0.3, k)
		return nil
	end) then return end

	local glow = spawnAsset(library:FindFirstChild("SnareGlow"), CFrame.new(center + UP * 0.12), cfg.radius * 2 / SNARE_BASE, true)
	if glow then
		enableAll(glow, "Pillar")
		table.insert(data.extraVFX, glow)
	end
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(center + UP), 1.2)
	playSound(SOUNDS.Impact, center, 0.75)
	playSound(SOUNDS.Transform, center, 0.6)
	shakeArea(center, 45, 1.6, 10, 0.05, 0.3)

	local captured = {}
	for _, target in ipairs(charactersInArea(character, center, cfg.radius, true)) do
		local targetRoot = target:FindFirstChild("HumanoidRootPart")
		if targetRoot then
			claimTarget(data, target)
			local hold = createAnchorHold(target)
			if hold then
				table.insert(data.holds, hold)
				local offset = Vector3.new(targetRoot.Position.X - center.X, 0, targetRoot.Position.Z - center.Z)
				table.insert(captured, {
					target = target,
					root = targetRoot,
					hold = hold,
					dir = offset.Magnitude > 0.2 and offset.Unit or flatDirection(root.Position, center, root.CFrame.LookVector),
					distance = offset.Magnitude,
					height = math.max(targetRoot.Position.Y - center.Y, standHeight(target)),
				})
				glowPulse(target, 0.05, cfg.cinchTime + cfg.bindTime + cfg.liftTime, 0.3)
			end
		end
	end

	local function valid(entry)
		if entry.hold.released then return false end
		local target = entry.target
		if isCharacterValid(target) and target:GetAttribute("TargetLockId") == data.targetLockId
			and not flagOn(target, "Invulnerable") and target:FindFirstChildOfClass("ForceField") == nil then
			return true
		end
		entry.hold.release(Vector3.zero)
		return false
	end
	local function prune()
		for index = #captured, 1, -1 do
			if not valid(captured[index]) then
				table.remove(captured, index)
			end
		end
	end

	rope.slack = 1
	rope.taut = true
	playSound(SOUNDS.Woosh, center, 0.8)
	local ticked = false
	if not waitFor(data, cfg.cinchTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.cinchTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.InOut)
		local ringRadius = cfg.radius + (cfg.cinchRadius - cfg.radius) * k
		rope.loop.radius = ringRadius
		rope.loop.center = center + UP * 0.3
		setFacing(data, character, center)
		for _, entry in ipairs(captured) do
			if valid(entry) then
				local d = math.min(entry.distance, math.max(ringRadius - 1.1, cfg.spacing))
				local position = center + UP * entry.height + entry.dir * d
				entry.hold.place(CFrame.lookAt(position, position - entry.dir))
			end
		end
		if not ticked and elapsed >= cfg.cinchTime * 0.55 then
			ticked = true
			for _, entry in ipairs(captured) do
				if valid(entry) then
					dealDamage(caster, entry.target, cfg.tickDamage, {screen = 0.3, color = TRUTH_GOLD})
				end
			end
			playSound(SOUNDS.Ribbon, center, 0.6)
		end
		return nil
	end) then return end

	prune()
	rope.loop.ground = false
	if #captured == 0 then
		authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(center + UP), 0.8)
		if glow then
			gracefullyCleanupVFX(takeVFX(data, glow))
		end
		clearFacing(data, character)
		retractRope(data, rope, 0.3)
		return
	end

	for _, entry in ipairs(captured) do
		applyTruth(data, entry.target)
	end
	local pillar = spawnAsset(library:FindFirstChild("SnareGlow"), CFrame.new(center + UP * 0.12), 1.1, true)
	if pillar then
		enableAll(pillar)
		table.insert(data.extraVFX, pillar)
	end
	local waist = 0
	for _, entry in ipairs(captured) do
		waist = math.max(waist, entry.height)
	end
	local aura = spawnAsset(library:FindFirstChild("TruthAura"), CFrame.new(center + UP * waist), 1, false)
	if aura then
		enableAll(aura)
		table.insert(data.extraVFX, aura)
	end
	authoredBurst(library:FindFirstChild("LashHit"), CFrame.new(center + UP * waist), 1.2)
	playSound(SOUNDS.Impact, center, 0.9)
	playSound(SOUNDS.Absorb, center, 0.7)
	shakeArea(center, 45, 2.2, 12, 0.02, 0.3)
	local count = #captured
	local function clusterOffset(index)
		if count == 1 then return Vector3.zero end
		local angle = (index - 1) * (2 * math.pi / count)
		return Vector3.new(math.cos(angle), 0, math.sin(angle)) * cfg.spacing
	end
	local function placeCluster(lift, k)
		for index, entry in ipairs(captured) do
			if valid(entry) then
				local packed = center + UP * entry.height + clusterOffset(index)
				local loose = center + UP * entry.height + entry.dir * math.max(math.min(entry.distance, cfg.cinchRadius - 1.1), cfg.spacing)
				local position = loose:Lerp(packed, k) + UP * lift
				entry.hold.place(CFrame.lookAt(position, position - entry.dir))
			end
		end
		rope.loop.center = center + UP * (waist * k + 0.3 * (1 - k) + lift)
		if aura and aura.Parent then
			aura:PivotTo(CFrame.new(center + UP * (waist + lift)) * CFrame.Angles(0, os.clock() * 2.4, 0))
		end
	end
	if not waitFor(data, cfg.bindTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.bindTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		rope.loop.radius = cfg.cinchRadius + (cfg.cinchRadius * 0.7 - cfg.cinchRadius) * k
		placeCluster(0, k)
		return nil
	end) then return end

	playSound(SOUNDS.Woosh, center, 1)
	playSound(SOUNDS.Swing, root.Position, 0.7)
	local liftHeight = cfg.liftHeight
	local headroom = workspace:Raycast(center + UP * waist, UP * (cfg.liftHeight + 4), groundParams(character))
	if headroom then
		liftHeight = math.max(2, headroom.Distance - 4)
	end
	if not waitFor(data, cfg.liftTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.liftTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		placeCluster(liftHeight * k, 1)
		return nil
	end) then return end
	if not waitFor(data, cfg.slamTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.slamTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		placeCluster(liftHeight * (1 - k), 1)
		return nil
	end) then return end

	prune()
	local slammed = {}
	for _, entry in ipairs(captured) do
		entry.hold.release(Vector3.zero)
		table.insert(slammed, entry)
	end
	for _, cleanup in ipairs(data.cleanups) do
		cleanup()
	end
	if glow then gracefullyCleanupVFX(takeVFX(data, glow)) end
	if pillar then gracefullyCleanupVFX(takeVFX(data, pillar)) end
	if aura then gracefullyCleanupVFX(takeVFX(data, aura)) end
	stomp(center, cfg.radius * 1.6)
	spawnCrater(center, cfg.radius * 0.55, 10, 16)
	spawnDebris(center + UP, 12, 0.5, 1.3)
	authoredBurst(library:FindFirstChild("LashHit"), CFrame.new(center + UP), 1.4)
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(center + UP * 2), 1.3)
	playSound(SOUNDS.Slam, center, 1.1)
	playSound(SOUNDS.RockBreak, center, 0.9)
	playSound(SOUNDS.Boom, center, 0.8)
	shakeArea(center, 75, 4.6, 11, 0.02, 0.55)
	flashArea(center)
	for _, entry in ipairs(slammed) do
		local target = entry.target
		if isCharacterValid(target) and dealDamage(caster, target, cfg.slamDamage, {screen = 0.85, color = TRUTH_GOLD}) > 0 and isCharacterValid(target) then
			glowPulse(target, 0.01, 0.06, 0.35)
			applyRagdoll(target, cfg.ragdoll, data)
			launch(entry.root, flatDirection(center, entry.root.Position, entry.dir) * cfg.knockback + UP * cfg.lift, data)
		end
	end
	clearFacing(data, character)
	rope.loop.radius = cfg.cinchRadius
	retractRope(data, rope, 0.3)
end

abilityHandlers.BraceletClash = function(caster, data)
	local cfg = ABILITY_CONFIG.BraceletClash
	local character = data.casterChar
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	if not character:GetAttribute("IsFlying") then stabilizeCharacter(character) end
	rootCaster(data, 0, false)
	-- ONE animation covers guard/charge -> CLASH at frame 33 (castTime 0.55) -> recoil
	playAnim(data, character, WW_ANIMS.BraceletClash, 0.06, 1)
	attachHandGlows(data, character, {"LeftHand", "RightHand"})
	playSound(SOUNDS.Charge, root.Position, 0.8)
	playSound(SOUNDS.Transform, root.Position, 0.5)
	local function chest()
		local torso = torsoOf(character)
		local base = torso and torso.Position or root.Position + UP
		return base + root.CFrame.LookVector * 1.4
	end
	local core = spawnAsset(library:FindFirstChild("ClashCore"), CFrame.new(chest()), 0.35, false)
	if core then
		enableAll(core, "Startup")
		table.insert(data.extraVFX, core)
	end
	glowPulse(character, cfg.castTime, 0.05, 0.3)
	if not castWindow(data, cfg.castTime, function(elapsed)
		local k = math.clamp(elapsed / cfg.castTime, 0, 1)
		if core and core.Parent then
			setModelScale(core, 0.35 + 0.45 * k)
			core:PivotTo(CFrame.new(chest()))
		end
		return nil
	end) then return end

	local origin = chest()
	local forward = flatDirection(root.Position, root.Position + root.CFrame.LookVector, root.CFrame.LookVector)
	if core then
		gracefullyCleanupVFX(takeVFX(data, core))
	end
	authoredBurst(library:FindFirstChild("ClashCore"), CFrame.new(origin), 1.1)
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(origin), 1.6)
	authoredBurst(library:FindFirstChild("ClashWave"), CFrame.lookAt(origin, origin + forward), cfg.radius * 1.2 / WAVE_BASE)
	local ground = getGroundPosition(root.Position, character)
	if (root.Position - ground).Magnitude < 10 then
		stomp(ground, cfg.radius * 2)
		spawnDebris(ground + UP, 12, 0.5, 1.2)
	end
	playSound(SOUNDS.SonicBoom, origin, 1)
	playSound(SOUNDS.Boom, origin, 0.9)
	playSound(SOUNDS.Impact, origin, 0.8)
	shakeArea(origin, 90, 5.5, 12, 0.02, 0.6)
	flashArea(origin)
	lampPulse(data, origin, cfg.radius + 30, 1.2, true)
	glowPulse(character, 0.01, 0.1, 0.4)
	for _, target in ipairs(charactersInArea(character, root.Position, cfg.radius)) do
		local targetRoot = target:FindFirstChild("HumanoidRootPart")
		if targetRoot and dealDamage(caster, target, cfg.damage, {screen = 0.9}) > 0 and isCharacterValid(target) then
			glowPulse(target, 0.01, 0.08, 0.4)
			applyRagdoll(target, cfg.ragdoll, data)
			local falloff = 1 - math.clamp((targetRoot.Position - root.Position).Magnitude / cfg.radius, 0, 1) * 0.4
			launch(targetRoot, flatDirection(root.Position, targetRoot.Position, forward) * cfg.knockback * falloff + UP * cfg.lift, data)
		end
	end
	dropHandGlows(data)
	rootCaster(data, 1, true)
	waitFor(data, 0.3)
end

abilityHandlers.Godkiller = function(caster, data, aimPoint)
	local cfg = ABILITY_CONFIG.Godkiller
	local character = data.casterChar
	local root = character:FindFirstChild("HumanoidRootPart")
	local hum = character:FindFirstChildOfClass("Humanoid")
	if not (root and hum) then return end
	local flying = character:GetAttribute("IsFlying") == true
	if not flying then stabilizeCharacter(character, aimPoint) end
	rootCaster(data, 0, false)
	local sword = mountSword(data, character)
	-- ONE animation: draw -> dash -> SLASH (frame 24) -> still -> flick/cuts -> CLEAVE (85) -> pillar
	playAnim(data, character, WW_ANIMS.Godkiller, 0.05, 1)
	playSound(SOUNDS.Transform, root.Position, 0.6)
	playSound(SOUNDS.Charge, root.Position, 0.45)
	if sword then
		authoredBurst(library:FindFirstChild("GodkillerGlint"), sword.CFrame, 0.9)
	end
	if not castWindow(data, cfg.castTime) then return end

	local startPosition = root.Position
	local toAim = aimPoint - startPosition
	local flat = Vector3.new(toAim.X, 0, toAim.Z)
	local facing = flat.Magnitude > 0.1 and flat.Unit or flatDirection(startPosition, startPosition, root.CFrame.LookVector)
	local direction = facing
	local distance = math.clamp(flat.Magnitude, cfg.minDash, cfg.range)
	if flying and toAim.Magnitude > 0.1 then
		direction = toAim.Unit
		distance = math.clamp(toAim.Magnitude, cfg.minDash, cfg.range)
	end
	local params = groundParams(character)
	local wall = workspace:Raycast(startPosition, direction * (distance + 2.5), params)
	if wall then
		distance = math.max(0, wall.Distance - 2.5)
	end
	local hover = standHeight(character)
	local releaseBody = lockBody(character)
	local cinematic = false
	local function finish()
		releaseBody()
		if cinematic then
			cinematic = false
			remoteEvent:FireClient(caster, "Cinematic", {active = false})
		end
		clearFacing(data, character)
	end
	data.onStop = finish

	local function grounded(position)
		if flying then return position end
		local floor = workspace:Raycast(position + UP * 4, Vector3.new(0, -14, 0), params)
		if floor then
			return Vector3.new(position.X, floor.Position.Y + hover, position.Z)
		end
		return position
	end
	local function moveTo(position, look)
		local lookDirection = look.Magnitude > 0.05 and look.Unit or facing
		if math.abs(lookDirection.Y) > 0.95 then
			lookDirection = (lookDirection + facing * 0.4).Unit
		end
		character:PivotTo(CFrame.lookAt(position, position + lookDirection))
	end
	local function kickDust(position)
		if flying then return end
		local ground = getGroundPosition(position, character)
		if (position - ground).Magnitude < 8 then
			authoredBurst(library:FindFirstChild("GodkillerDust"), CFrame.new(ground + UP * 0.2), 0.55, true)
		end
	end

	authoredBurst(library:FindFirstChild("GodkillerStep"), CFrame.lookAt(startPosition, startPosition + direction), 1)
	playSound(SOUNDS.Woosh, startPosition, 1)
	playSound(SOUNDS.Swing, startPosition, 0.7)
	local travel = cfg.dashTime -- fixed so the single animation stays in sync
	local last, lastDust = startPosition, startPosition
	local hit
	local dashElapsed = 0
	if not waitFor(data, travel, function(elapsed)
		dashElapsed = elapsed
		local k = TweenService:GetValue(math.clamp(elapsed / travel, 0, 1), Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
		local position = grounded(startPosition + direction * (distance * k))
		moveTo(position, facing)
		if (position - lastDust).Magnitude > 7 then
			lastDust = position
			kickDust(position)
		end
		for _, candidate in ipairs(CharacterIndex.Get()) do
			if candidate ~= character and canBeGrabbed(candidate) then
				local candidateRoot = candidate:FindFirstChild("HumanoidRootPart")
				if candidateRoot and segmentDistance(candidateRoot.Position, last, position) <= cfg.contactRadius then
					hit = candidate
					break
				end
			end
		end
		last = position
		return hit ~= nil
	end) then return end

	if not hit then
		kickDust(root.Position)
		playSound(SOUNDS.Swing, root.Position, 0.5)
		finish()
		data.onStop = nil
		scaleCooldown(caster, data.abilityName, cfg.missCooldownScale)
		rootCaster(data, 1, true)
		waitFor(data, 0.12)
		return
	end

	local target = hit
	local targetRoot = target:FindFirstChild("HumanoidRootPart")
	local function stop()
		stopAbility(caster.UserId, data.instanceKey, true)
	end
	local targetConnections = watchTarget(data, target, stop)
	claimTarget(data, target)
	local hold = createAnchorHold(target)
	if not hold then return end
	table.insert(data.holds, hold)
	local function held()
		return isCharacterValid(target) and target:GetAttribute("TargetLockId") == data.targetLockId
			and not flagOn(target, "Invulnerable") and target:FindFirstChildOfClass("ForceField") == nil
	end
	local function torsoPoint()
		local torso = torsoOf(target)
		return torso and torso.Position or targetRoot.Position
	end
	cinematic = true
	remoteEvent:FireClient(caster, "Cinematic", {active = true, target = target})
	local victimTrack = AnimationManager:PlayAnimation(target, WW_ANIMS.Victim, 0.06, 1, 0.6)
	if victimTrack then
		table.insert(data.animTracks, victimTrack)
	end
	local frozen = CFrame.lookAt(targetRoot.Position, targetRoot.Position - facing)
	hold.place(frozen)
	-- hold the contact until the fixed dash window ends so the animation's slash lines up
	if not waitFor(data, math.max(0, travel - dashElapsed), function()
		if not held() then
			stop()
			return true
		end
		return nil
	end) or not held() then return end

	local function strike(strength, damage)
		local point = torsoPoint()
		if dealDamage(caster, target, damage, {screen = 0.3 + 0.3 * strength}) > 0 then
			authoredBurst(library:FindFirstChild("GodkillerHit"), CFrame.new(point), 0.45 + 0.3 * strength)
			playSound(SOUNDS.Impact, point, 0.6 + 0.3 * strength)
			glowPulse(target, 0.01, 0.03, 0.18)
		end
		remoteEvent:FireClient(caster, "CinematicHit", strength)
		shakeCharacter(character, 0.5 + strength, 12, 0.02, 0.18)
	end

	slashArc(slashFrame(torsoPoint(), facing, 0.12), cfg.slashScale * 1.3, 1)
	strike(0.8, cfg.contactDamage)
	playSound(SOUNDS.Swing, root.Position, 1)
	local passFrom = root.Position
	local passTo = grounded(targetRoot.Position + facing * cfg.passDistance)
	local passVector = passTo - passFrom
	if passVector.Magnitude > 0.1 then
		local blocked = workspace:Raycast(passFrom, passVector, params)
		if blocked then
			passTo = blocked.Position - passVector.Unit * 2
		end
	end
	if not waitFor(data, cfg.passTime, function(elapsed)
		if not held() then
			stop()
			return true
		end
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.passTime, 0, 1), Enum.EasingStyle.Quart, Enum.EasingDirection.Out)
		moveTo(passFrom:Lerp(passTo, k), facing)
		return nil
	end) or not held() then return end
	kickDust(passTo)
	authoredBurst(library:FindFirstChild("GodkillerStep"), CFrame.lookAt(passTo, passTo + facing), 0.6)

	playSound(SOUNDS.Whisper, passTo, 0.6)
	local tilts = cfg.cutTilts
	glowPulse(target, 0.05, cfg.stillTime + #tilts * cfg.cutGap, 0.25)
	applyTargetScreenEffect(target, cfg.stillTime + 0.6, TRUTH_GOLD)
	local marks = {}
	local nextMark = 0
	if not waitFor(data, cfg.stillTime, function(elapsed)
		if not held() then
			stop()
			return true
		end
		while #marks < #tilts and elapsed >= nextMark do
			local index = #marks + 1
			local approach = CFrame.fromAxisAngle(UP, (index - (#tilts + 1) / 2) * 0.4):VectorToWorldSpace(facing)
			marks[index] = cutMark(data, slashFrame(torsoPoint(), approach, tilts[index]), cfg.slashScale) or false
			playSound(SOUNDS.Swing, torsoPoint(), 0.35)
			nextMark += cfg.stillTime * 0.6 / #tilts
		end
		return nil
	end) or not held() then return end

	if sword and sword.Parent then
		authoredBurst(library:FindFirstChild("GodkillerGlint"), sword.CFrame, 1.1)
	end
	playSound(SOUNDS.Charge, root.Position, 0.5)
	for index = 1, #tilts do
		local mark = marks[index]
		if mark then
			releaseCut(data, mark, (index % 2 == 0) and 0.9 or -0.9)
		end
		strike(0.6, cfg.cutDamage)
		local jolt = mark and mark.cframe.RightVector * 0.5 or facing * 0.5
		hold.place(frozen + jolt)
		if not waitFor(data, cfg.cutGap, function(elapsed)
			if not held() then
				stop()
				return true
			end
			if elapsed > cfg.cutGap * 0.5 then
				hold.place(frozen)
			end
			return nil
		end) or not held() then return end
	end

	local towardTarget = flatDirection(root.Position, targetRoot.Position, -facing)
	moveTo(root.Position, towardTarget)
	local plantPoint = getGroundPosition(root.Position + towardTarget * 1.8, character)
	local targetGround = findFloor(targetRoot.Position + UP * 2, target) or getGroundPosition(targetRoot.Position, target)
	authoredBurst(library:FindFirstChild("GodkillerSparks"), CFrame.new(plantPoint + UP * 0.2), 0.6, true)
	stomp(plantPoint, 10)
	playSound(SOUNDS.Slam, plantPoint, 0.8)
	playSound(SOUNDS.RockBreak, plantPoint, 0.7)
	shakeArea(plantPoint, 40, 2, 12, 0.02, 0.25)
	local fissureSteps = 4
	local stepsDone = 0
	if not waitFor(data, cfg.fissureTime, function(elapsed)
		if not held() then
			stop()
			return true
		end
		while stepsDone < fissureSteps and elapsed >= (stepsDone / fissureSteps) * cfg.fissureTime do
			stepsDone += 1
			local point = plantPoint:Lerp(targetGround, stepsDone / (fissureSteps + 1))
			authoredBurst(library:FindFirstChild("GodkillerSparks"), CFrame.new(point + UP * 0.2), 0.45, true)
			authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(point + UP * 0.6), 0.35)
		end
		return nil
	end) or not held() then return end

	unwatch(targetConnections)
	if victimTrack then
		pcall(function()
			victimTrack:Stop(0.05)
		end)
	end
	hold.release(Vector3.zero)
	local pillar = spawnAsset(library:FindFirstChild("SnareGlow"), CFrame.new(targetGround + UP * 0.12), cfg.pillarScale, true)
	if pillar then
		enableAll(pillar)
		table.insert(data.extraVFX, pillar)
	end
	local strikePoint = torsoPoint()
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(strikePoint), 1.8)
	authoredBurst(library:FindFirstChild("GodkillerHit"), CFrame.new(strikePoint), 1.3)
	authoredBurst(library:FindFirstChild("ClashWave"), CFrame.fromMatrix(targetGround + UP * 0.3, Vector3.xAxis, Vector3.zAxis), cfg.pillarRing * 2 / WAVE_BASE)
	spawnCrater(targetGround, 6, 10, 14)
	spawnDebris(targetGround + UP, 12, 0.5, 1.3)
	playSound(SOUNDS.Boom, targetGround, 1)
	playSound(SOUNDS.Impact, targetGround, 1)
	playSound(SOUNDS.SonicBoom, targetGround, 0.6)
	playSound(SOUNDS.Transform, targetGround, 0.8)
	shakeArea(targetGround, 80, 5, 11, 0.02, 0.6)
	flashArea(targetGround)
	lampPulse(data, targetGround, 40, 1.2, true)
	remoteEvent:FireClient(caster, "CinematicHit", 1.6)
	if dealDamage(caster, target, cfg.pillarDamage, {screen = 0.95, color = TRUTH_GOLD}) > 0 and isCharacterValid(target) then
		glowPulse(target, 0.01, 0.08, 0.4)
		applyRagdoll(target, cfg.ragdoll, data)
		launch(targetRoot, UP * cfg.pillarLift + towardTarget * 4, data)
	end
	if not waitFor(data, 0.45) then return end
	if sword and sword.Parent then
		authoredBurst(library:FindFirstChild("GodkillerGlint"), sword.CFrame, 1)
	end
	finish()
	data.onStop = nil
	rootCaster(data, 1, true)
	waitFor(data, 0.15)
end

abilityHandlers.GoldenEagle = function(caster, data, aimPoint)
	local cfg = ABILITY_CONFIG.GoldenEagle
	local character = data.casterChar
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local flying = character:GetAttribute("IsFlying") == true
	if not flying then stabilizeCharacter(character, aimPoint) end
	rootCaster(data, 0, false)
	-- ONE animation: wings open -> rise -> feather barrage -> BIG feather (frame 79) -> fold -> descend
	playAnim(data, character, WW_ANIMS.GoldenEagle, 0.08, 1)
	attachHandGlows(data, character, {"LeftHand", "RightHand"})
	playSound(SOUNDS.Transform, root.Position, 0.7)
	playSound(SOUNDS.Woosh, root.Position, 0.8)
	local wings = mountWings(data, character, cfg.wingScale)
	local torso = torsoOf(character)
	local function backPoint()
		local basis = torso and torso.Parent and torso.CFrame or root.CFrame
		return basis * CFrame.new(0, 0.6, 1.2)
	end
	authoredBurst(library:FindFirstChild("DivineGlint"), backPoint(), 1.2)
	glowPulse(character, 0.15, cfg.castTime, 0.35)
	local function poseWings(fold, flap)
		if not wings then return end
		for _, joint in ipairs(wings.joints) do
			if joint.motor.Parent then
				joint.motor.C0 = joint.open * CFrame.Angles(0, joint.side * cfg.foldAngle * fold, joint.side * flap)
			end
		end
	end
	poseWings(1, 0)
	if not castWindow(data, cfg.castTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.castTime, 0, 1), Enum.EasingStyle.Back, Enum.EasingDirection.Out)
		poseWings(1 - k, 0)
		return nil
	end) then return end
	poseWings(0, 0)
	playSound(SOUNDS.Swing, root.Position, 0.8)

	local releaseBody = lockBody(character)
	data.onStop = function()
		releaseBody()
		clearFacing(data, character)
	end
	local basePosition = root.Position
	local hoverHeight = flying and 0 or cfg.hoverHeight
	local ceiling = workspace:Raycast(basePosition, UP * (hoverHeight + 4), groundParams(character))
	if ceiling then
		hoverHeight = math.max(0, ceiling.Distance - 4)
	end
	local airPosition = basePosition + UP * hoverHeight
	local look = flatDirection(basePosition, aimPoint, root.CFrame.LookVector)
	local function moveCaster(position)
		character:PivotTo(CFrame.lookAt(position, position + look))
	end
	if not waitFor(data, cfg.riseTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.riseTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		moveCaster(basePosition:Lerp(airPosition, k))
		poseWings(0, -cfg.flapAngle * math.sin(k * math.pi))
		return nil
	end) then return end

	local params = groundParams(character)
	local aimFrom = airPosition + UP * 1.2
	local toAim = aimPoint - aimFrom
	local distance = math.clamp(toAim.Magnitude, 10, cfg.range)
	local forward = toAim.Magnitude > 0.1 and toAim.Unit or look
	local right = forward:Cross(UP)
	right = right.Magnitude > 0.1 and right.Unit or root.CFrame.RightVector

	local function featherImpact(point, target, big, travelVector)
		if big then
			authoredBurst(library:FindFirstChild("GodkillerHit"), CFrame.new(point), 1)
			authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(point), 0.9)
			playSound(SOUNDS.Impact, point, 1)
			playSound(SOUNDS.Boom, point, 0.6)
			shakeArea(point, 40, 2.4, 12, 0.02, 0.3)
		else
			authoredBurst(library:FindFirstChild("LashHit"), CFrame.new(point), 0.45)
			playSound(SOUNDS.Impact, point, 0.45)
		end
		if not target then return end
		local targetRoot = target:FindFirstChild("HumanoidRootPart")
		local amount = big and cfg.bigDamage or cfg.featherDamage
		if targetRoot and dealDamage(caster, target, amount, {screen = big and 0.7 or 0.2, silent = not big}) > 0 and isCharacterValid(target) then
			glowPulse(target, 0.01, 0.03, big and 0.3 or 0.15)
			if big then
				applyRagdoll(target, cfg.bigRagdoll, data)
				launch(targetRoot, flatDirection(Vector3.zero, travelVector, look) * cfg.bigKnockback + UP * cfg.bigLift, data)
			else
				applySlow(target, cfg.slow, cfg.slowTime)
			end
		end
	end

	local function wingTip(side)
		local basis = torso and torso.Parent and torso.CFrame or root.CFrame
		return (basis * CFrame.new(side * 3.2 * (cfg.wingScale / 0.62), 1.4, 0.9)).Position
	end

	local feathers = {}
	local started = os.clock()
	local total = cfg.feathers + 1
	for i = 1, total do
		local big = i == total
		table.insert(feathers, {
			launchAt = started + (i - 1) * cfg.stagger + (big and 0.12 or 0),
			side = (i % 2 == 0) and 1 or -1,
			fan = big and 0 or ((i - 1) / math.max(cfg.feathers - 1, 1) * 2 - 1) * cfg.spread,
			big = big,
		})
	end
	local pending = #feathers
	while pending > 0 do
		RunService.Heartbeat:Wait()
		if not isLive(data) then return end
		local now = os.clock()
		pending = 0
		poseWings(0, cfg.flapAngle * math.sin((now - started) * 22))
		for _, feather in ipairs(feathers) do
			if not feather.done then
				pending += 1
				if now >= feather.launchAt then
					if not feather.from then
						local from = feather.big and (aimFrom + look * 1.5) or wingTip(feather.side)
						local fanDirection = CFrame.fromAxisAngle(UP, feather.fan):VectorToWorldSpace(forward)
						local goal = from + fanDirection * distance
						local best = cfg.homingRadius
						for _, candidate in ipairs(CharacterIndex.Get()) do
							if candidate ~= character and canBeHit(candidate) then
								local candidateRoot = candidate:FindFirstChild("HumanoidRootPart")
								if candidateRoot then
									local gap = segmentDistance(candidateRoot.Position, from, goal)
									if gap < best then
										best = gap
										feather.lock = candidate
									end
								end
							end
						end
						feather.from = from
						feather.goal = goal
						feather.last = from
						feather.control = from + right * feather.side * 3.5 + UP * 2.5 + fanDirection * (distance * 0.2)
						feather.duration = math.clamp(distance / cfg.speed, cfg.minTravel, cfg.maxTravel) * (feather.big and 1.15 or 1)
						feather.model = spawnAsset(library:FindFirstChild(feather.big and "EagleFeatherBig" or "EagleFeather"), CFrame.new(from), feather.big and 1 or 1.4, false)
						if feather.model then
							enableAll(feather.model)
							table.insert(data.extraVFX, feather.model)
						end
						playSound(feather.big and SOUNDS.Woosh or SOUNDS.Swing, from, feather.big and 1 or 0.4)
					end
					local goal = feather.goal
					if feather.lock and isCharacterValid(feather.lock) then
						local lockTorso = torsoOf(feather.lock)
						if lockTorso then
							goal = lockTorso.Position
						end
					end
					local alpha = math.clamp((now - feather.launchAt) / feather.duration, 0, 1)
					local position = quadBezier(feather.from, feather.control, goal, alpha)
					local travelVector = position - feather.last
					local impactPoint, impactTarget
					if travelVector.Magnitude > 1e-3 then
						local wallHit = workspace:Raycast(feather.last, travelVector, params)
						local segmentEnd = wallHit and wallHit.Position or position
						if wallHit then
							impactPoint = wallHit.Position
						end
						for _, candidate in ipairs(CharacterIndex.Get()) do
							if candidate ~= character and canBeHit(candidate) then
								local candidateRoot = candidate:FindFirstChild("HumanoidRootPart")
								if candidateRoot and segmentDistance(candidateRoot.Position, feather.last, segmentEnd) <= cfg.hitRadius then
									impactTarget = candidate
									impactPoint = candidateRoot.Position
									break
								end
							end
						end
					end
					if not impactPoint and alpha >= 1 then
						impactPoint = position
						if feather.lock and canBeHit(feather.lock) then
							impactTarget = feather.lock
						end
					end
					if impactPoint then
						feather.done = true
						if feather.model then
							gracefullyCleanupVFX(takeVFX(data, feather.model))
						end
						featherImpact(impactPoint, impactTarget, feather.big, travelVector.Magnitude > 1e-3 and travelVector or forward)
					elseif feather.model and feather.model.Parent then
						local heading = travelVector.Magnitude > 1e-3 and travelVector.Unit or forward
						feather.model:PivotTo(CFrame.lookAt(position, position + heading) * CFrame.Angles(-math.pi / 2, 0, 0))
					end
					feather.last = position
				end
			end
		end
	end

	-- keep the fire phase a fixed length so the animation's fold lines up
	if not waitFor(data, math.max(0, cfg.fireTime - (os.clock() - started)), function()
		poseWings(0, cfg.flapAngle * math.sin((os.clock() - started) * 22))
		return nil
	end) then return end
	playSound(SOUNDS.Woosh, root.Position, 0.6)
	if not waitFor(data, cfg.foldTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.foldTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		poseWings(k, 0)
		return nil
	end) then return end
	if wings then
		authoredBurst(library:FindFirstChild("DivineGlint"), backPoint(), 0.8)
		gracefullyCleanupVFX(takeVFX(data, wings.model))
	end
	dropHandGlows(data)
	if not waitFor(data, cfg.descendTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.descendTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.InOut)
		moveCaster(airPosition:Lerp(basePosition, k))
		return nil
	end) then return end
	releaseBody()
	clearFacing(data, character)
	data.onStop = nil
	rootCaster(data, 1, true)
end

validators.WrathOfZeus = function(_, casterChar, target)
	if lineClear(casterChar, target, ABILITY_CONFIG.WrathOfZeus.range + RANGE_TOLERANCE) then return target end
	return nil
end

abilityHandlers.WrathOfZeus = function(caster, data, target)
	local cfg = ABILITY_CONFIG.WrathOfZeus
	local character = data.casterChar
	local root = character:FindFirstChild("HumanoidRootPart")
	local targetRoot = target:FindFirstChild("HumanoidRootPart")
	local targetHum = target:FindFirstChildOfClass("Humanoid")
	if not (root and targetRoot and targetHum) then return end
	local function stop()
		stopAbility(caster.UserId, data.instanceKey, true)
	end
	local targetConnections = watchTarget(data, target, stop)
	local function torsoPoint()
		local torso = torsoOf(target)
		return torso and torso.Position or targetRoot.Position
	end
	local function held()
		return isCharacterValid(target) and target:GetAttribute("TargetLockId") == data.targetLockId
			and not flagOn(target, "Invulnerable") and target:FindFirstChildOfClass("ForceField") == nil
	end
	local function handsCenter()
		local left = character:FindFirstChild("LeftHand")
		local right = character:FindFirstChild("RightHand")
		if left and right then
			return (left.Position + right.Position) * 0.5
		end
		return root.Position + UP * 1.5
	end

	local savedCollisions
	local anchored = false
	local hold
	local function restoreCaster()
		if savedCollisions then
			for part, state in pairs(savedCollisions) do
				if part.Parent then
					part.CanCollide, part.CanQuery, part.CanTouch = state[1], state[2], state[3]
				end
			end
			savedCollisions = nil
		end
		if anchored and root.Parent then
			root.Anchored = false
			root.AssemblyLinearVelocity = Vector3.zero
			root.AssemblyAngularVelocity = Vector3.zero
			anchored = false
		end
	end
	data.onStop = function()
		restoreCaster()
		clearFacing(data, character)
	end

	if not character:GetAttribute("IsFlying") then stabilizeCharacter(character, targetRoot.Position) end
	rootCaster(data, 0, false)
	-- ONE animation: storm call -> rise -> 3 bolts -> beam RELEASE (frame 101) -> torrent -> FINALE (179) -> descend
	playAnim(data, character, WW_ANIMS.WrathOfZeus, 0.08, 1)
	attachHandGlows(data, character, {"LeftHand", "RightHand"})
	playSound(SOUNDS.ZapCharge, root.Position, 0.6)
	playSound(SOUNDS.Transform, root.Position, 0.5)
	if not castWindow(data, cfg.castTime, function()
		if targetRoot.Parent then
			setFacing(data, character, targetRoot.Position)
		end
		return nil
	end) then return end
	if not canBeAffected(target) or not lineClear(character, target, cfg.range + RANGE_TOLERANCE) then
		data.fizzled = true
		return
	end

	savedCollisions = {}
	for _, part in ipairs(character:GetDescendants()) do
		if part:IsA("BasePart") then
			savedCollisions[part] = {part.CanCollide, part.CanQuery, part.CanTouch}
			part.CanCollide = false
			part.CanTouch = false
		end
	end
	root.Anchored = true
	anchored = true
	local basePosition = root.Position
	local forward = flatDirection(basePosition, targetRoot.Position, root.CFrame.LookVector)
	local riseHeight = cfg.riseHeight
	local ceiling = workspace:Raycast(basePosition, UP * (cfg.riseHeight + 4), groundParams(character))
	if ceiling then
		riseHeight = math.max(0, ceiling.Distance - 4)
	end
	local risePosition = basePosition + UP * riseHeight
	local function moveCaster(position)
		local look = targetRoot.Parent and flatDirection(position, targetRoot.Position, forward) or forward
		character:PivotTo(CFrame.lookAt(position, position + look))
	end
	if not waitFor(data, cfg.riseTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.riseTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		moveCaster(basePosition:Lerp(risePosition, k))
		return nil
	end) then return end

	for i = 1, cfg.strikes do
		local point = handsCenter()
		local final = i == cfg.strikes
		authoredBurst(library:FindFirstChild("ZeusBolt"), CFrame.new(point), 0.9 + i * 0.15, true)
		authoredBurst(library:FindFirstChild("ZeusSpark"), CFrame.new(point), 0.8 + i * 0.1)
		playSound(final and SOUNDS.Thunder or SOUNDS.Bolt, point, final and 1 or 0.75)
		playSound(SOUNDS.Zap, point, 0.6)
		shakeArea(point, 70, 1.4 + i * 0.6, 12, 0.02, 0.3)
		flashArea(point)
		lampPulse(data, point, 45, 0.6, final)
		glowPulse(character, 0.01, 0.06, 0.25, ZEUS_FILL, ZEUS_OUTLINE)
		if not waitFor(data, cfg.strikeGap, function(elapsed)
			moveCaster(risePosition + UP * (math.sin(elapsed * 14) * 0.12))
			return nil
		end) then return end
	end
	if not canBeAffected(target) or not lineClear(character, target, cfg.range + RANGE_TOLERANCE) then
		data.fizzled = true
		return
	end

	claimTarget(data, target)
	hold = createHold(target)
	if not hold then return end
	table.insert(data.holds, hold)
	local suspended = targetRoot.Position + UP * 1.5
	local victimTrack = AnimationManager:PlayAnimation(target, WW_ANIMS.Victim, 0.08, 1, 1.2)
	if victimTrack then
		table.insert(data.animTracks, victimTrack)
	end
	local beam = createZeusBeam(cfg.beamScale)
	if beam then
		table.insert(data.extraVFX, beam.model)
		local casterTorso = torsoOf(character)
		local targetTorso = torsoOf(target)
		if casterTorso and targetTorso then
			beam.bind(casterTorso, CFrame.new(0, 0.3, -1.8), targetTorso, CFrame.identity)
		end
		beam.place(handsCenter() + forward * 0.8, torsoPoint())
	end
	local current = playSound(SOUNDS.Current, handsCenter(), 0.85)
	table.insert(data.extraVFX, current)
	authoredBurst(library:FindFirstChild("ZeusSpark"), CFrame.new(torsoPoint()), 1)
	applyTargetScreenEffect(target, cfg.torrentTime, ZEUS_BLUE)
	local chains = {}
	local candidates = charactersInArea(character, targetRoot.Position, cfg.chainRadius)
	table.sort(candidates, function(a, b)
		local ar, br = a:FindFirstChild("HumanoidRootPart"), b:FindFirstChild("HumanoidRootPart")
		return (ar.Position - targetRoot.Position).Magnitude < (br.Position - targetRoot.Position).Magnitude
	end)
	for _, other in ipairs(candidates) do
		if other ~= target and #chains < cfg.chainCount then
			local link = createZeusBeam(cfg.chainScale)
			if link then
				table.insert(data.extraVFX, link.model)
				local fromTorso = torsoOf(target)
				local toTorso = torsoOf(other)
				if fromTorso and toTorso then
					link.bind(fromTorso, CFrame.identity, toTorso, CFrame.identity)
				end
				table.insert(chains, {target = other, beam = link})
			end
		end
	end

	local nextTick = 0
	if not waitFor(data, cfg.torrentTime, function(elapsed)
		if not held() then
			stop()
			return true
		end
		setFacing(data, character, targetRoot.Position)
		moveCaster(risePosition)
		local origin = handsCenter() + forward * 0.8
		local torso = torsoPoint()
		local ramp = math.clamp(elapsed / 0.18, 0, 1)
		if beam then
			beam.place(origin, torso)
			beam.width(ramp * (0.9 + 0.2 * math.sin(elapsed * 40)))
		end
		hold.align.Position = suspended + Vector3.new(math.random() - 0.5, math.random() - 0.5, math.random() - 0.5) * 0.3
		hold.orientation.CFrame = CFrame.lookAt(Vector3.zero, -forward)
		for _, chain in ipairs(chains) do
			local otherTorso = torsoOf(chain.target)
			if otherTorso and canBeHit(chain.target) then
				chain.beam.place(torso, otherTorso.Position)
				chain.beam.width(ramp * (0.8 + 0.3 * math.sin(elapsed * 55)))
			else
				chain.beam.width(0)
			end
		end
		if elapsed >= nextTick then
			nextTick += cfg.tickInterval
			if dealDamage(caster, target, cfg.tickDamage, {silent = true}) > 0 then
				authoredBurst(library:FindFirstChild("ZeusSpark"), CFrame.new(torso), 0.6)
				glowPulse(target, 0.01, 0.03, 0.15, ZEUS_FILL, ZEUS_OUTLINE)
				shakeCharacter(target, 1.4, 14, 0.02, 0.15)
			end
			shakeCharacter(character, 0.6, 12, 0.02, 0.12)
			for _, chain in ipairs(chains) do
				if canBeHit(chain.target) then
					if dealDamage(caster, chain.target, cfg.chainDamage, {silent = true}) > 0 then
						glowPulse(chain.target, 0.01, 0.03, 0.15, ZEUS_FILL, ZEUS_OUTLINE)
						applySlow(chain.target, 0.4, cfg.tickInterval + 0.3)
					end
				end
			end
		end
		return nil
	end) or not held() then return end

	unwatch(targetConnections)
	if beam then
		beam.collapse(0.15)
		takeVFX(data, beam.model)
	end
	for _, chain in ipairs(chains) do
		chain.beam.collapse(0.12)
		takeVFX(data, chain.beam.model)
	end
	gracefullyCleanupVFX(takeVFX(data, current))
	if victimTrack then
		pcall(function()
			victimTrack:Stop(0.05)
		end)
	end
	local strikeTorso = torsoPoint()
	local impact = getGroundPosition(targetRoot.Position, target)
	hold.release(Vector3.zero)
	authoredBurst(library:FindFirstChild("ZeusBolt"), CFrame.new(impact), 2.2, true)
	authoredBurst(library:FindFirstChild("ZeusStrike"), CFrame.new(impact + UP * 0.5), 1.6)
	authoredBurst(library:FindFirstChild("ZeusBurst"), CFrame.new(strikeTorso), 1.4)
	authoredBurst(library:FindFirstChild("DivineGlint"), CFrame.new(strikeTorso), 1.4)
	if (strikeTorso - impact).Magnitude < 10 then
		stomp(impact, cfg.splashRadius * 2)
		spawnCrater(impact, 8, 12, 18)
		spawnDebris(impact + UP, 14, 0.6, 1.4)
	end
	playSound(SOUNDS.Thunder, impact, 1.2)
	playSound(SOUNDS.Boom, impact, 1)
	playSound(SOUNDS.Zap, impact, 0.9)
	shakeArea(impact, 100, 6, 11, 0.02, 0.7)
	flashArea(impact)
	lampPulse(data, impact, cfg.splashRadius + 34, 1.6, true)
	local away = flatDirection(risePosition, impact, forward)
	if dealDamage(caster, target, cfg.finaleDamage, {screen = 0.95, color = ZEUS_BLUE}) > 0 and isCharacterValid(target) then
		glowPulse(target, 0.01, 0.08, 0.4, ZEUS_FILL, ZEUS_OUTLINE)
		applyRagdoll(target, cfg.ragdoll, data)
		launch(targetRoot, away * cfg.knockback + UP * cfg.lift, data)
	end
	for _, other in ipairs(charactersInArea(character, impact, cfg.splashRadius)) do
		if other ~= target then
			local otherRoot = other:FindFirstChild("HumanoidRootPart")
			if otherRoot and dealDamage(caster, other, cfg.splashDamage, {screen = 0.6, color = ZEUS_BLUE}) > 0 and isCharacterValid(other) then
				glowPulse(other, 0.01, 0.05, 0.3, ZEUS_FILL, ZEUS_OUTLINE)
				applyRagdoll(other, cfg.splashRagdoll, data)
				launch(otherRoot, flatDirection(impact, otherRoot.Position, away) * cfg.splashKnockback + UP * cfg.splashLift, data)
			end
		end
	end

	dropHandGlows(data)
	if not waitFor(data, cfg.descendTime, function(elapsed)
		local k = TweenService:GetValue(math.clamp(elapsed / cfg.descendTime, 0, 1), Enum.EasingStyle.Quad, Enum.EasingDirection.InOut)
		moveCaster(risePosition:Lerp(basePosition, k))
		return nil
	end) then return end
	restoreCaster()
	clearFacing(data, character)
	rootCaster(data, 1, true)
	waitFor(data, 0.12)
end

remoteEvent.OnServerEvent:Connect(function(caster, action, abilityName, targetData)
	if type(action) ~= "string" then return end
	if ABILITY_CONFIG[action] and abilityName ~= "Start" and abilityName ~= "End" then
		targetData = type(abilityName) == "table" and (abilityName.TargetCharacter or abilityName.TargetPosition) or abilityName
		abilityName = action
		action = "Start"
	end
	local casterId = caster.UserId

	if action == "Sync" then
		sendCooldownSnapshot(caster)
		return
	end
	if type(abilityName) ~= "string" then return end

	if action == "End" then
		local perUser = activeAbilities[casterId]
		if perUser then
			local keys = {}
			for key, entry in pairs(perUser) do
				if entry.abilityName == abilityName and not (entry.committed and isCharacterValid(entry.casterChar)) then
					table.insert(keys, key)
				end
			end
			for _, key in ipairs(keys) do
				stopAbility(casterId, key, false)
			end
		end
		return
	end

	local cfg = ABILITY_CONFIG[abilityName]
	if action ~= "Start" or not cfg or not abilityHandlers[abilityName] then return end

	local function reject()
		remoteEvent:FireClient(caster, "ForceStop", abilityName)
	end
	local casterChar = caster.Character
	if not canCast(casterChar) then return reject() end
	if caster:GetAttribute("SelectedCharacter") ~= "WonderWoman" then return reject() end
	if casterChar:GetAttribute("IsFlying") and not cfg.flightAllowed then return reject() end
	if typeof(targetData) ~= cfg.targetKind then return reject() end
	if typeof(targetData) == "Instance" then
		local valid = targetData:IsDescendantOf(workspace)
			and targetData:FindFirstChildOfClass("Humanoid") ~= nil
			and targetData:FindFirstChild("HumanoidRootPart") ~= nil
		if not valid or targetData == casterChar then return reject() end
	elseif targetData ~= targetData or targetData.Magnitude > 100000 then
		return reject()
	end
	if isOnCooldown(casterId, abilityName) then
		reject()
		sendCooldownSnapshot(caster)
		return
	end
	if not isInRange(casterChar, abilityName, targetData) then return reject() end
	if typeof(targetData) == "Instance" and not canBeAffected(targetData) then return reject() end
	local validator = validators[abilityName]
	if validator then
		targetData = validator(caster, casterChar, targetData)
		if targetData == nil then return reject() end
	end

	if activeAbilities[casterId] and next(activeAbilities[casterId]) then return reject() end
	local instanceKey = abilityName
	activeAbilities[casterId] = activeAbilities[casterId] or {}
	if activeAbilities[casterId][instanceKey] then return reject() end
	abilityInstanceCounter += 1

	local data = {
		abilityName = abilityName,
		instanceKey = instanceKey,
		casterChar = casterChar,
		unstoppable = cfg.unstoppable == true,
		armorPending = cfg.armorOnLand == true and cfg.unstoppable ~= true,
		casterLockId = abilityName .. "_Caster_" .. abilityInstanceCounter .. "_" .. tostring(math.random()),
		targetLockId = abilityName .. "_Target_" .. abilityInstanceCounter .. "_" .. tostring(math.random()),
		targets = {},
		extraVFX = {},
		handGlows = {},
		connections = {},
		animTracks = {},
		lampEchoes = {},
		ropes = {},
		holds = {},
		cleanups = {},
	}
	if not CombatRules.claimPriority(casterChar, targetData, cfg.radius, data.casterLockId, cfg.castTime) then return reject() end
	activeAbilities[casterId][instanceKey] = data
	startCooldown(casterId, abilityName)

	captureBaseStats(casterChar)
	casterChar:SetAttribute("AbilityLockId", data.casterLockId)
	MoveLock.apply(casterChar, data.casterLockId, {passive = true, duration = MAX_ABILITY_LIFETIME})
	setCharacterFlag(casterChar, "AbilityActive", true)
	if data.unstoppable then
		CombatRules.grantArmor(casterChar, data.casterLockId, MAX_ABILITY_LIFETIME)
	end

	local casterHum = casterChar:FindFirstChildOfClass("Humanoid")
	if casterHum then
		table.insert(data.connections, casterHum.Died:Connect(function()
			stopAbility(casterId, instanceKey, false)
		end))
	end
	setCharacterFlag(casterChar, "BeingAttacked", false)
	for _, flagName in ipairs({"BeingAttacked", "Ragdoll"}) do
		local flag = casterChar:FindFirstChild(flagName)
		if flag and flag:IsA("BoolValue") then
			table.insert(data.connections, flag.Changed:Connect(function(value)
				if value and (not data.committed or data.armorPending) and CombatRules.interrupts(casterChar) then
					stopAbility(casterId, instanceKey, data.committed == true)
				end
			end))
		end
	end

	data.mainThread = task.spawn(function()
		local ok, err = pcall(abilityHandlers[abilityName], caster, data, targetData)
		if not ok then
			warn(string.format("[WonderWoman] %s errored: %s", abilityName, tostring(err)))
			stopAbility(casterId, instanceKey, false)
			return
		end
		stopAbility(casterId, instanceKey, not data.fizzled)
	end)

	task.delay(MAX_ABILITY_LIFETIME, function()
		if activeAbilities[casterId] and activeAbilities[casterId][instanceKey] == data then
			warn(string.format("[WonderWoman] %s outlived its window and was force-stopped.", abilityName))
			stopAbility(casterId, instanceKey, false)
		end
	end)
end)

local function stopEverything(player)
	local live = activeAbilities[player.UserId]
	if live then
		local keys = {}
		for key in pairs(live) do
			table.insert(keys, key)
		end
		for _, key in ipairs(keys) do
			stopAbility(player.UserId, key, false)
		end
	end
end

local function bindCharacter(player, character)
	local humanoid = character:WaitForChild("Humanoid", 10)
	if humanoid and humanoid:IsA("Humanoid") then
		humanoid.Died:Connect(function()
			stopEverything(player)
		end)
	end
end

local function bindPlayer(player)
	player.CharacterAdded:Connect(function(character)
		cooldowns[player.UserId] = nil
		task.delay(1.5, function()
			if player.Parent then
				remoteEvent:FireClient(player, "CooldownClear")
			end
		end)
		bindCharacter(player, character)
	end)
	player.CharacterRemoving:Connect(function()
		stopEverything(player)
	end)
	player:GetAttributeChangedSignal("SelectedCharacter"):Connect(function()
		if player:GetAttribute("SelectedCharacter") ~= "WonderWoman" then
			stopEverything(player)
		end
	end)
	if player.Character then
		task.spawn(bindCharacter, player, player.Character)
	end
end

for _, player in ipairs(Players:GetPlayers()) do
	bindPlayer(player)
end
Players.PlayerAdded:Connect(bindPlayer)

Players.PlayerRemoving:Connect(function(player)
	stopEverything(player)
	activeAbilities[player.UserId] = nil
	cooldowns[player.UserId] = nil
end)
