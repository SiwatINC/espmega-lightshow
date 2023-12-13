from src.espmega_lightshow.drivers import ESPMegaLightDriver, ESPMegaStandaloneLightDriver, ESPMegaLightGrid, HomeAssistantLightDriver
from homeassistant_api import Client as HomeAssistantClient
from secrets_storage import ha_api_key
from time import sleep  

# This is an example of how to use the HomeAssistantLightDriver

# Define and instantiate home assistant client
ha_client = HomeAssistantClient("http://192.168.0.26/api", ha_api_key)
# Define and instantiate the driver
driver = HomeAssistantLightDriver(ha_client, "light.laboratory_ceiling_light")
# Cycle the light on and off
while True:
    driver.set_light_state(True)
    sleep(1)
    driver.set_light_state(False)
    sleep(1)