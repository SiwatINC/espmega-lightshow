from abc import ABC
from espmega.espmega_r3 import ESPMega_standalone as ESPMega
import json
# This is the base class for all physical light drivers


class LightDriver(ABC):
    # The init function should take in any parameters needed to initialize the driver
    # This function should not raise any exceptions if the driver is not able to be initialized
    # Instead, it should set the driver to a state where it is not able to be controlled
    conntected: bool = False
    state: bool = False
    color: tuple = (0, 0, 0)
    brightness: int = 0

    def __init__(self, **kwargs):
        pass

    def set_light_state(self, state: bool) -> None:
        pass

    def get_light_state(self) -> int:
        # Returns 0 if the light is off, 1 if the light is on
        # Return 2 if the light is on but is not able to be controlled
        # Return 3 if the light is off but is not able to be controlled
        pass

    def is_connected(self) -> bool:
        return self.conntected
    
    def get_exception(self) -> str:
        if self.conntected:
            return None
        return self.exception

    @staticmethod
    def get_driver_properties() -> dict:
        # Standard properties:
        #   name: The name of the driver
        #   support_brightness: Whether the driver supports brightness control
        #   support_color: Whether the driver supports color control
        pass

    def set_brightness(self, brightness: float) -> None:
        pass

    def get_brightness(self) -> float:
        pass

    def set_color(self, color: tuple) -> None:
        pass

    def get_color(self) -> tuple:
        pass


class ESPMegaLightDriver(LightDriver):
    rapid_mode: bool = False

    def __init__(self, controller: ESPMega, pwm_channel: int) -> int:
        self.controller = controller
        self.pwm_channel = pwm_channel
        if controller is None:
            self.conntected = False
            self.exception = "Controller is not connected."
        self.conntected = True

    def set_light_state(self, state: bool) -> None:
        if not self.conntected:
            self.state = state
        else:
            self.controller.digital_write(self.pwm_channel, state)

    def get_light_state(self) -> bool:
        if self.conntected:
            self.state = self.controller.get_pwm_state(self.pwm_channel)
        return self.state + 2 * (not self.conntected)

    @staticmethod
    def get_driver_properties() -> dict:
        return {
            "name": "ESPMega",
            "support_brightness": False,
            "support_color": False
        }


class ESPMegaStandaloneLightDriver(ESPMegaLightDriver):
    def __init__(self, base_topic: str,pwm_channel: int, light_server: str, light_server_port: int) -> dict:
        self.base_topic = base_topic
        self.light_server = light_server
        self.light_server_port = light_server_port
        self.pwm_channel = pwm_channel
        self.state = False
        try:
            self.controller = ESPMega(
                base_topic, light_server, light_server_port)
        except Exception as e:
            self.controller = None
            self.conntected = False
            self.exception = e
        self.conntected = True

    @staticmethod
    def get_driver_properties() -> dict:
        return {
            "name": "ESPMega Standalone",
            "support_brightness": False,
            "support_color": False
        }


class ESPMegaLightGrid:
    def __init__(self, light_server: str, light_server_port: int, rows: int = 0, columns: int = 0, rapid_mode: bool = False, design_mode: bool = False):
        self.rows = rows
        self.columns = columns
        self.lights: list = [None] * rows * columns
        self.drivers = {}
        self.light_server = light_server
        self.light_server_port = light_server_port
        self.design_mode = design_mode

    def assign_physical_light(self, row: int, column: int, physical_light: LightDriver):
        self.lights[row * self.columns + column] = physical_light

    def get_physical_light(self, row, column):
        return self.lights[row * self.columns + column]

    def set_light_state(self, row: int, column: int, state: bool) -> None:
        physical_light = self.get_physical_light(row, column)
        if not self.design_mode:
            physical_light.set_light_state(state)

    def get_light_state(self, row: int, column: int):
        physical_light = self.get_physical_light(row, column)
        return physical_light.get_light_state()

    def read_light_map(self, light_map: list) -> list:
        self.light_map = light_map
        self.rows = len(light_map)
        self.columns = len(light_map[0])
        self.lights = [None] * self.rows * self.columns
        self.controllers = {}  # Dictionary to store existing controllers
        self.failed_controllers = {}  # Dictionary to store failed controllers
        self.connected_controllers = {}  # Dictionary to store connected controllers
        for row_index, row in enumerate(light_map):
            for column_index, light in enumerate(row):
                if self.design_mode:
                    self.connected_controllers[light["base_topic"]] = None
                    self.assign_physical_light(row_index, column_index, None)
                    continue
                if light is None:
                    self.assign_physical_light(row_index, column_index, None)
                else:
                    base_topic = light["base_topic"]
                    pwm_id = light["pwm_id"]
                    # Create a mapping of base_topic to controller
                    if base_topic not in self.drivers:
                        if not self.design_mode:
                            driver = ESPMegaStandaloneLightDriver(base_topic, self.light_server, self.light_server_port)
                        if driver.is_connected():
                            self.drivers[base_topic] = driver
                        else:
                            self.failed_drivers[base_topic] = driver.get_exception()
                    else:
                        controller = self.drivers[base_topic].controller
                        driver = ESPMegaLightDriver(controller, pwm_id)
                    self.assign_physical_light(row_index, column_index, driver)
        # Return a list of connected drivers list and failed drivers list
        return [self.connected_drivers, self.failed_drivers]
    def read_light_map_from_file(self, filename: str):
        try:
            with open(filename, "r") as file:
                light_map = json.load(file)
            # Check if the light map is valid
            if len(light_map) == 0:
                raise Exception("Light map cannot be empty.")
            if len(light_map[0]) == 0:
                raise Exception("Light map cannot be empty.")
            for row in light_map:
                if len(row) != len(light_map[0]):
                    raise Exception(
                        "All rows in the light map must have the same length.")
                for column in row:
                    if column != None:
                        if "base_topic" not in column:
                            raise Exception(
                                "The base_topic field is missing from a light.")
                        if "pwm_id" not in column:
                            raise Exception(
                                "The pwm_id field is missing from a light.")
                        if type(column["base_topic"]) != str:
                            raise Exception(
                                "The base_topic field must be a string.")
                        if type(column["pwm_id"]) != int:
                            raise Exception(
                                "The pwm_id field must be an integer.")
            self.read_light_map(light_map)
        except FileNotFoundError:
            raise Exception("The light map file does not exist.")