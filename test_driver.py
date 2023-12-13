from src.espmega_lightshow.drivers import ESPMegaLightDriver, ESPMegaStandaloneLightDriver, ESPMegaLightGrid
from time import sleep

# Define and instantiate the driver
driver = ESPMegaStandaloneLightDriver("/espmega/ProR3", 0, "192.168.0.26", 1883)
driver.set_light_state(True)

# Define and instantiate a slave driver
slave_driver = ESPMegaLightDriver(driver.controller, 1)
slave_driver.set_light_state(True)

# Define and instantiate a light grid
light_grid = ESPMegaLightGrid("192.168.0.26",1883, 2, 2, False, False)
light_grid.assign_physical_light(0, 0, driver)
light_grid.assign_physical_light(0, 1, slave_driver)

while True:
    light_grid.set_light_state(0, 0, True)
    light_grid.set_light_state(0, 1, False)
    sleep(1)
    light_grid.set_light_state(0, 0, False)
    light_grid.set_light_state(0, 1, True)
    sleep(1)