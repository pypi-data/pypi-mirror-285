# This version requires pioreactor >= 24.7.18

from pioreactor.background_jobs.monitor import Monitor

try:
    from temperature_expansion_kit_plugin import Thermostat
except ImportError:
    from pioreactor.automations.temperature.thermostat import Thermostat

try:
    from temperature_expansion_kit_plugin import TemperatureAutomationJobWithProbe as TemperatureAutomationJob
except ImportError:
    from pioreactor.background_jobs.temperature_automation import TemperatureAutomationJob


TemperatureAutomationJob.MAX_TEMP_TO_REDUCE_HEATING = 83.5
TemperatureAutomationJob.MAX_TEMP_TO_DISABLE_HEATING = 85.0
TemperatureAutomationJob.MAX_TEMP_TO_SHUTDOWN = 87.0

TemperatureAutomationJob.INFERENCE_EVERY_N_SECONDS = 5 * 60 # PWM is on for just over half the time, instead of ~1/3

Monitor.MAX_TEMP_TO_SHUTDOWN = 87.0
Thermostat.MAX_TARGET_TEMP = 90.0

