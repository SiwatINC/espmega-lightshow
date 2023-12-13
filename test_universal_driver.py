from src.espmega_lightshow.drivers import UniversalLightGrid
from secrets_storage import ha_api_key
from time import sleep
example_universal_grid_map = [[{"driver": "espmega", "light_server": "192.168.0.26", "light_server_port": 1883, "base_topic": "/espmega/ProR3", "pwm_id": 0}, {"driver": "homeassistant", "api_url": "http://192.168.0.26/api", "api_key": ha_api_key, "entity_id": "light.laboratory_ceiling_light"}], [
    {"driver": "espmega", "light_server": "192.168.0.26", "light_server_port": 1883, "base_topic": "/espmega/ProR3", "pwm_id": 1}, {"driver": "homeassistant", "api_url": "http://192.168.0.26/api", "api_key": ha_api_key, "entity_id": "light.laboratory_light_strip"}]]
grid = UniversalLightGrid()
grid.read_light_map(example_universal_grid_map)

# Cycle the light on and off in order to test the driver
# Note that this is a 2x2 grid, we will go clockwise
while True:
    grid.set_light_state(0, 0, True)
    grid.set_light_state(1, 0, False)
    sleep(1)
    grid.set_light_state(0, 0, False)
    grid.set_light_state(0, 1, True)
    sleep(1)
    grid.set_light_state(0, 1, False)
    grid.set_light_state(1, 1, True)
    sleep(1)
    grid.set_light_state(1, 1, False)
    grid.set_light_state(1, 0, True)
    sleep(1)
