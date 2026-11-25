-- CAN1 telemetry logging. AuxLinear1..4 must be free of local ADC assignments.
local frontBrake = Sensor.new("AuxLinear1")
local rearBrake = Sensor.new("AuxLinear2")
local fork = Sensor.new("AuxLinear3")
local shock = Sensor.new("AuxLinear4")
frontBrake:setTimeout(250)
rearBrake:setTimeout(250)
fork:setTimeout(250)
shock:setTimeout(250)

local brakeAge = Timer.new()
local missing = 0.0 / 0.0

local function centi(data, i)
    local raw = data[i] + 256 * data[i + 1]
    if raw >= 32768 then raw = raw - 65536 end
    return raw * 0.01
end

local function suspension(bus, id, dlc, data)
    if dlc ~= 8 then return end
    fork:set(centi(data, 1))
    shock:set(centi(data, 3))
end

local function brakesAndAttitude(bus, id, dlc, data)
    if dlc ~= 8 then return end
    frontBrake:set(centi(data, 1))
    rearBrake:set(centi(data, 3))
    setLuaGauge(1, centi(data, 5))
    setLuaGauge(2, centi(data, 7))
    brakeAge:reset()
end

setLuaGauge(1, missing)
setLuaGauge(2, missing)
canRxAdd(1, 0x300, suspension)
canRxAdd(1, 0x301, brakesAndAttitude)
setTickRate(200)

function onTick()
    if brakeAge:getElapsedSeconds() >= 0.250 then
        setLuaGauge(1, missing)
        setLuaGauge(2, missing)
    end
end
