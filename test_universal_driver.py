from src.espmega_lightshow.drivers import UniversalLightGrid
from secrets_storage import ha_api_key
example_universal_grid_map = [[{"driver": "espmega", "light_server": "192.168.0.26", "light_server_port": 1883, "base_topic": "/espmega/ProR3", "pwm_id": 0}, {"driver": "homeassistant", "api_url": "http://192.168.0.26/api", "api_key": ha_api_key, "entity_id": "light.light0"}], [
    {"driver": "espmega", "light_server": "192.168.0.26", "light_server_port": 1883, "base_topic": "/espmega/ProR3", "pwm_id": 1}, {"driver": "homeassistant", "api_url": "http://192.168.0.26/api", "api_key": ha_api_key, "entity_id": "light.light0"}]]
grid = UniversalLightGrid()
grid.read_light_map(example_universal_grid_map)
