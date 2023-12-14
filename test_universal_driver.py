from src.espmega_lightshow.drivers import UniversalLightGrid
from time import sleep
map_path = "C:\\Users\\siwat\\Nextcloud\\Documents\\m21_map_emg.json"
grid = UniversalLightGrid()
grid.read_light_map_from_file(map_path)

sleep(5)

# Check if light at 0,0 is connected
print(grid.get_light_state(0, 0))

# Cycle the light on and off in order to test the driver
# Note that this is a 2x2 grid, we will go clockwise
# while True:
#     grid.set_light_state(0, 0, True)
#     grid.set_light_state(1, 0, False)
#     sleep(1)
#     grid.set_light_state(0, 0, False)
#     grid.set_light_state(0, 1, True)
#     sleep(1)
#     grid.set_light_state(0, 1, False)
#     grid.set_light_state(1, 1, True)
#     sleep(1)
#     grid.set_light_state(1, 1, False)
#     grid.set_light_state(1, 0, True)
#     sleep(1)
