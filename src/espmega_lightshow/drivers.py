from abc import ABC
from espmega.espmega_r3 import ESPMega_standalone as ESPMega
import json
from typing import Optional

# This is the base class for all physical light drivers
class LightDriver(ABC):
    LIGHT_STATE_OFF = 0
    LIGHT_STATE_ON = 1
    LIGHT_STATE_OFF_UNCONTROLLED = 2
    LIGHT_STATE_ON_UNCONTROLLED = 3
    connected: bool = False
    state: bool = False
    color: tuple = (0, 0, 0)
    brightness: int = 0
    exception: Optional[str] = None

    def __init__(self, **kwargs):
        # The init function should take in any parameters needed to initialize the driver
        # This function should not raise any exceptions if the driver is not able to be initialized
        # Instead, it should set the driver to a state where it is not able to be controlled
        pass

    def set_light_state(self, state: bool) -> None:
        # This function should set the light to the given state
        pass

    def get_light_state(self) -> int:
        # This function should return the current state of the light
        # Returns 0 if the light is off, 1 if the light is on
        # Return 2 if the light is off but is not able to be controlled
        # Return 3 if the light is on but is not able to be controlled
        pass

    @staticmethod
    def invert_light_state(state: int) -> int:
        # This function should invert the given light state
        if(state == LightDriver.LIGHT_STATE_OFF):
            return LightDriver.LIGHT_STATE_ON
        elif(state == LightDriver.LIGHT_STATE_ON):
            return LightDriver.LIGHT_STATE_OFF
        elif(state == LightDriver.LIGHT_STATE_OFF_UNCONTROLLED):
            return LightDriver.LIGHT_STATE_ON_UNCONTROLLED
        elif(state == LightDriver.LIGHT_STATE_ON_UNCONTROLLED):
            return LightDriver.LIGHT_STATE_OFF_UNCONTROLLED

    def state_to_multistate(self, state: int) -> int:
        # This function should convert the given state to a multistate
        # A state is a binary value, either on or off
        # A multistate holds both states, on and off, and whether they are controlled

        # Returns 0 if the light is off, 1 if the light is on
        # Return 2 if the light is off but is not able to be controlled
        # Return 3 if the light is on but is not able to be controlled
        if self.connected:
            return state
        else:
            return state + 2

    def is_connected(self) -> bool:
        # This function should return whether the driver is connected to the light
        return self.connected
    
    def get_exception(self) -> Optional[str]:
        # This function should return the exception that caused the driver to be disconnected
        if self.connected:
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
        # This function should set the brightness of the light
        # brightness is a float between 0 and 4095
        pass

    def get_brightness(self) -> float:
        # This function should return the current brightness of the light
        # brightness is a float between 0 and 4095
        pass

    def set_color(self, color: tuple) -> None:
        # This function should set the color of the light
        # color is a tuple of 3 integers between 0 and 4095
        pass

    def get_color(self) -> tuple:
        # This function should return the current color of the light
        # color is a tuple of 3 integers between 0 and 4095
        pass


class ESPMegaLightDriver(LightDriver):
    rapid_mode: bool = False

    def __init__(self, controller: ESPMega, pwm_channel: int) -> int:
        self.controller = controller
        self.pwm_channel = pwm_channel
        if controller is None:
            self.connected = False
            self.exception = "Controller is not connected."
        else:
            self.connected = True

    def set_light_state(self, state: bool) -> None:
        if not self.connected:
            self.state = state
        else:
            self.controller.digital_write(self.pwm_channel, state)

    def get_light_state(self) -> bool:
        if self.connected:
            self.state = self.controller.get_pwm_state(self.pwm_channel)
        return self.state + 2 * (not self.connected)

    @staticmethod
    def get_driver_properties() -> dict:
        return {
            "name": "ESPMega",
            "support_brightness": False,
            "support_color": False
        }


class ESPMegaStandaloneLightDriver(ESPMegaLightDriver):
    def __init__(self, base_topic: str,pwm_channel: int, light_server: str, light_server_port: int, rapid_mode: bool = False) -> dict:
        self.base_topic = base_topic
        self.light_server = light_server
        self.light_server_port = light_server_port
        self.pwm_channel = pwm_channel
        self.rapid_mode = rapid_mode
        self.state = False
        self.connected = False
        try:
            self.controller = ESPMega(
                base_topic, light_server, light_server_port)
            if rapid_mode:
                self.controller.set_rapid_mode()
            print("Connected to controller.")
            self.connected = True
        except Exception as e:
            self.controller = None
            self.exception = e
            self.connected = False
    def close(self):
        if self.connected and self.rapid_mode:
            self.controller.disable_rapid_response_mode()
    @staticmethod
    def get_driver_properties() -> dict:
        return {
            "name": "ESPMega Standalone",
            "support_brightness": False,
            "support_color": False
        }

class DummyLightDriver(LightDriver):
    def __init__(self, **kwargs):
        self.connected = True
        self.state = False

    def set_light_state(self, state: bool) -> None:
        self.state = state

    def get_light_state(self) -> bool:
        return self.state

    @staticmethod
    def get_driver_properties() -> dict:
        return {
            "name": "Dummy",
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

    def is_installed(self, row: int, column: int) -> bool:
        # True if the light is not a NoneType
        return not isinstance(self.lights[row * self.columns + column], type(None))

    def assign_physical_light(self, row: int, column: int, physical_light: Optional[LightDriver]):
        self.lights[row * self.columns + column] = physical_light

    def mark_light_disappeared(self, row: int, column: int):
        self.lights[row * self.columns + column] = None

    def get_physical_light(self, row, column) -> Optional[LightDriver]:
        return self.lights[row * self.columns + column]

    def set_light_state(self, row: int, column: int, state: bool) -> None:
        physical_light = self.get_physical_light(row, column)
        if not self.design_mode:
            physical_light.set_light_state(state)

    def get_light_state(self, row: int, column: int):
        physical_light = self.get_physical_light(row, column)
        return physical_light.get_light_state()

    def read_light_map(self, light_map: list) -> list:
        self.initialize_light_map(light_map)
        for row_index, row in enumerate(light_map):
            for column_index, light in enumerate(row):
                self._assign_light(row_index, column_index, light)
        return [self.connected_drivers, self.failed_drivers]

    def initialize_light_map(self, light_map):
        self.light_map = light_map
        self.rows = len(light_map)
        self.columns = len(light_map[0])
        self.lights = [None] * self.rows * self.columns
        self.failed_drivers = {}  # Dictionary to store failed controllers
        self.connected_drivers = {}  # Dictionary to store connected controllers

    def _assign_light(self, row_index, column_index, light):
        print(f"Assigning light at {row_index}, {column_index}, its base topic is {light['base_topic']}, The controller loaded are {self.drivers}")
        if self.design_mode:
            self.connected_drivers[light["base_topic"]] = None
            self.assign_physical_light(row_index, column_index, DummyLightDriver())
            return
        if light is None:
            self.assign_physical_light(row_index, column_index, None)
        else:
            self._assign_light_with_driver(row_index, column_index, light)

    def _assign_light_with_driver(self, row_index, column_index, light):
        base_topic = light["base_topic"]
        pwm_id = light["pwm_id"]
        if base_topic not in self.drivers:
            driver = self._create_new_driver(base_topic, pwm_id)
        else:
            controller = self.drivers[base_topic].controller
            driver = ESPMegaLightDriver(controller, pwm_id)
        self.assign_physical_light(row_index, column_index, driver)

    def _create_new_driver(self, base_topic: str, pwm_id: int):
        if not self.design_mode:
            print("Creating new driver")
            driver = ESPMegaStandaloneLightDriver(base_topic, pwm_id, self.light_server, self.light_server_port)
            print("Created new driver")
        if driver.is_connected():
            print(f"Adding driver {base_topic} to connected drivers")
            self.connected_drivers[base_topic] = driver
        else:
            print(f"Adding driver {base_topic} to failed drivers, its exception is {driver.get_exception()}")
            self.failed_drivers[base_topic] = driver.get_exception()
        self.drivers[base_topic] = driver
        return driver

    def read_light_map_from_file(self, filename: str):
        try:
            with open(filename, "r") as file:
                light_map = json.load(file)
            
            ESPMegaLightGrid._validate_light_map(light_map)
            self.read_light_map(light_map)
            
        except FileNotFoundError:
            raise FileNotFoundError("The light map file does not exist.")

    @staticmethod
    def _validate_light_map(light_map):
        if len(light_map) == 0:
            raise ValueError("Light map cannot be empty.")
        
        if len(light_map[0]) == 0:
            raise ValueError("Light map cannot be empty.")
        
        for row in light_map:
            ESPMegaLightGrid._validate_row(row, light_map[0])

    @staticmethod
    def _validate_row(row, reference_row):
        if len(row) != len(reference_row):
            raise ValueError("All rows in the light map must have the same length.")
        
        for column in row:
            ESPMegaLightGrid._validate_column(column)

    @staticmethod
    def _validate_column(column):
        if column is not None:
            if "base_topic" not in column:
                raise ValueError("The base_topic field is missing from a light.")
            
            if "pwm_id" not in column:
                raise ValueError("The pwm_id field is missing from a light.")
            
            if not isinstance(column["base_topic"], str):
                raise ValueError("The base_topic field must be a string.")
            
            if not isinstance(column["pwm_id"], int):
                raise ValueError("The pwm_id field must be an integer.")
