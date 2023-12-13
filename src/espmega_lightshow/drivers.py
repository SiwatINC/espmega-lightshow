from abc import ABC
from espmega.espmega_r3 import ESPMega_standalone, ESPMega
import json
from typing import Optional
homeassistant_api_available = True
try :
    from homeassistant_api import Client as HomeAssistantClient
    from homeassistant_api import errors as HomeAssistantErrors
except ImportError:
    homeassistant_api_available = False
    HomeAssistantClient = any
    HomeAssistantErrors = any
from paho.mqtt.client import Client as MQTTClient
from threading import Thread

class DriverDependencyNotMetError(Exception):
    pass

class PackageManager:
    @staticmethod
    def get_available_drivers() -> dict:
        # This function should return a dictionary of driver names to driver classes
        # The driver classes should be subclasses of LightDriver
        # The driver names should be strings
        # The driver classes should be able to be initialized without any parameters
        drivers = {}
        driver['disabled'] = []
        # Check if homeassistant_api is available
        if homeassistant_api_available:
            drivers["homeassistant"] = HomeAssistantLightDriver
        drivers["espmega"] = ESPMegaLightDriver
    @staticmethod
    def get_config_options():
        config_option = {}
        config_option["disabled"] = []
        if homeassistant_api_available:
            config_option["homeassistant"] = HomeAssistantLightDriver.get_driver_properties()["configuration_parameters"]
        config_option["espmega"] = ESPMegaLightDriver.get_driver_properties()["configuration_parameters"]
        return config_option
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
            "support_color": False,
            "configuration_parameters": ["light_server", "light_server_port","base_topic", "pwm_id"]
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
            self.controller = ESPMega_standalone(
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
            "support_color": False,
            "configuration_parameters": ["light_server", "light_server_port", "pwm_id"]
        }
    
# This class manage a group of ESPMegaLightDriver and ESPMegaStandaloneLightDriver
# It also allows for multiple ESPMegaLightDriver and ESPMegaStandaloneLightDriver connected to different servers
# It manages the connection to the servers and the controllers to ensure that there is only one connection to each server
# It also manages the controllers to ensure that there is only one controller per base topic
class ESPMegaMultiController:
    def __init__(self):
        # Dictionary of server ip to mqtt connection
        self.mqtt_connections = {}
        # Dictionary of tuple of server ip, port, and base topic to controller
        self.controllers = {}
        # Dictionary of tuple of server ip, port, base topic, and pwm channel to ESPMegaLightDriver
        self.drivers = {}
    def get_controller(self, base_topic: str, light_server: str, light_server_port: int, rapid_mode: bool = False) -> ESPMega:
        # Check if the there is a connection to the server
        print(f"Getting controller for {base_topic}, {light_server}, {light_server_port}")
        if (light_server, light_server_port) not in self.mqtt_connections:
            print(f"Creating connection for {base_topic}, {light_server}, {light_server_port}")
            # If there is no connection, create one
            self.mqtt_connections[(light_server, light_server_port)] = MQTTClient()
            try:
                self.mqtt_connections[(light_server, light_server_port)].connect(light_server, light_server_port)
                self.mqtt_connections[(light_server, light_server_port)].loop_start()
                print(f"Connected to {light_server}:{light_server_port}")
            except Exception as e:
                print(f"Failed to connect to {light_server}:{light_server_port}")
                print(e)
                return None
        # Check if there is a controller for the base topic and server
        if (light_server, light_server_port, base_topic) not in self.controllers:
            # If there is no controller, create one
            # Note that the connection to the server is already established at this point
            # The only thing that can cause the controller to fail is if a controller does not exist for the base topic
            try:
                self.controllers[(light_server, light_server_port, base_topic)] = ESPMega(base_topic, self.mqtt_connections[(light_server, light_server_port)])
            except Exception as e:
                print(e)
                # If the controller fails to connect, return None as the controller does not exist
                return None
            if rapid_mode:
                self.controllers[(light_server, light_server_port, base_topic)].enable_rapid_response_mode()
        # Return the controller
        return self.controllers[(light_server, light_server_port, base_topic)]
    def remove_controller(self, base_topic: str, light_server: str, light_server_port: int):
        # Check if there is a controller for the base topic and server
        if (light_server, light_server_port, base_topic) in self.controllers:
            # Disable rapid response mode
            self.controllers[(light_server, light_server_port, base_topic)].disable_rapid_response_mode()
            # If there is a controller, check if there is any other controllers for the server
            if sum([1 for key in self.controllers.keys() if key[0] == light_server and key[1] == light_server_port]) == 1:
                # If there is no other controllers for the server, close the connection
                self.mqtt_connections[(light_server, light_server_port)].disconnect()
                del self.mqtt_connections[(light_server, light_server_port)]
            # Delete the controller
            del self.controllers[(light_server, light_server_port, base_topic)]

class DummyLightDriver(LightDriver):
    def __init__(self, offline: bool = False):
        self.connected = True
        self.state = False
        self.offline = offline
    def set_light_state(self, state: bool) -> None:
        self.state = state

    def get_light_state(self) -> int:
        return self.state + 2 * self.offline

    @staticmethod
    def get_driver_properties() -> dict:
        return {
            "name": "Dummy",
            "support_brightness": False,
            "support_color": False,
            "configuration_parameters": []
        }

class HomeAssistantLightDriver(LightDriver):
    def __init__(self, ha: HomeAssistantClient, entity_id: str):
        # Connect to Home Assistant
        self.ha = ha
        self.entity_id = entity_id
        self.command_waiting = False
        try:
            self.light_api = ha.get_domain("light")
        except Exception as e:
            print(e)
            self.connected = False
            self.exception = e
            return
        except HomeAssistantErrors.UnauthorizedError:
            self.connected = False
            self.exception = "Unauthorized"
            return
        self.connected = True

    def _set_state_thread(self, state: bool):
        if self.command_waiting:
            return
        try:
            self.command_waiting = True
            self.light_api.turn_on(entity_id=self.entity_id) if state else self.light_api.turn_off(entity_id=self.entity_id)
            self.command_waiting = False
        except Exception as e:
            print(e)
            self.connected = False
            self.exception = e
            self.command_waiting = False

    def set_light_state(self, state: bool) -> None:
        self.state = state
        Thread(target=self._set_state_thread, args=(state,)).start()

    def get_light_state(self) -> bool:
        return self.state_to_multistate(self.state)

    @staticmethod
    def get_driver_properties() -> dict:
        return {
            "name": "Home Assistant",
            "support_brightness": False,
            "support_color": False,
            "configuration_parameters": ["api_url", "api_key", "entity_id"]
        }

class HomeAssistantMultiServer:
    def __init__(self):
        # Dictionary of a tuple of api url and api key to Home Assistant client
        self.ha_clients = {}
    def get_ha_client(self, api_url: str, api_key: str) -> HomeAssistantClient:
        # If homeassistant_api is not available, raise an exception
        if not homeassistant_api_available:
            raise DriverDependencyNotMetError("The homeassistant_api package is not installed but is used in the loaded light map.\nPlease install the package by running 'pip install homeassistant_api'\nNote that this requires Visual Studio Build Tools 2015 to be installed.")
        # Check if there is a Home Assistant client for the api url and api key
        if (api_url, api_key) not in self.ha_clients:
            # If there is no Home Assistant client, create one
            try:
                self.ha_clients[(api_url, api_key)] = HomeAssistantClient(api_url, api_key)
            except Exception as e:
                print(e)
                return None
            # Return the Home Assistant client
        return self.ha_clients[(api_url, api_key)]

class LightGrid(ABC):
    def __init__(self, rows: int = 0, columns: int = 0, design_mode: bool = False):
        self.rows = rows
        self.columns = columns
        self.lights: list = [None] * rows * columns
        self.design_mode = design_mode
    def is_installed(self, row: int, column: int) -> bool:
        # Check if the light is enabled
        # True if the light is not a NoneType
        return not isinstance(self.lights[row * self.columns + column], type(None))
    def assign_physical_light(self, row: int, column: int, physical_light: Optional[LightDriver]):
        self.lights[row * self.columns + column] = physical_light
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
        # This function should read the light map and assign the lights to the grid
        # The light map is a 2D array of light objects
        # The light objects are dictionaries with fields varying by driver
        # The light map should be validated before being passed to this function
        # This function should return a list of connected drivers and a list of failed drivers
        # The connected drivers list should be a dictionary of base topics to drivers
        # The failed drivers list should be a dictionary of base topics to exceptions
        pass
    def initialize_light_map(self, light_map):
        # This function should initialize the light map
        # It should set the rows, columns, lights, failed drivers, and connected drivers
        pass

    def _validate_light_map(self, light_map):
        # This function should validate the light map
        pass

    @staticmethod
    def _validate_light_map(light_map):
        # This function should validate the light map
        pass

    @staticmethod
    def _validate_row(row, reference_row):
        # This function should validate the row
        pass
    @staticmethod
    def _validate_column(column):
        # This function should validate the column
        pass

class ESPMegaLightGrid(LightGrid):
    def __init__(self, light_server: str, light_server_port: int, rows: int = 0, columns: int = 0, rapid_mode: bool = False, design_mode: bool = False):
        self.rows = rows
        self.columns = columns
        self.lights: list = [None] * rows * columns
        self.drivers = {}
        self.light_server = light_server
        self.light_server_port = light_server_port
        self.design_mode = design_mode

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
            driver = ESPMegaStandaloneLightDriver(base_topic, pwm_id, self.light_server, self.light_server_port)
        if driver.is_connected():
            self.connected_drivers[base_topic] = driver
        else:
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

# A universal light grid is a light grid that can use any driver
class UniversalLightGrid(LightGrid):
    def __init__(self, rows: int = 0, columns: int = 0, design_mode: bool = False):
        self.rows = rows
        self.columns = columns
        self.lights: list = [None] * rows * columns
        self.driver_types: list = [None] * rows * columns
        self.design_mode = design_mode
        self.espmega_driver_bank = ESPMegaMultiController()
        self.ha_server_bank = HomeAssistantMultiServer()
    def read_light_map(self, light_map: list) -> list:
        # First we will validate the light map
        self._validate_light_map(light_map)
        # Then we will initialize the light map
        self.initialize_light_map(light_map)
        for row_index, row in enumerate(light_map):
            for column_index, light in enumerate(row):
                # light is a dictionary with fields varying by driver
                # Is the light disabled?
                if light is None:
                    self.assign_physical_light(row_index, column_index, None)
                    continue
                # Are we in design mode?
                # If we are in design mode, we don't need to connect to the drivers, so we can just assign a dummy driver
                if self.design_mode:
                    self.assign_physical_light(row_index, column_index, DummyLightDriver())
                    continue
                # Let's switch on the driver field
                driver_type = light["driver"]
                print(light)
                # If the driver is espmega, we utilize the ESPMegaMultiController to manage the controllers
                if driver_type == "espmega":
                    controller = self.espmega_driver_bank.get_controller(light["base_topic"], light["light_server"], light["light_server_port"])
                    print(f"Controller: {controller}, {light['base_topic']}")
                    # The controller might be None if the connection failed, we will assign a dummy driver in offline mode
                    if isinstance(controller, type(None)):
                        self.assign_physical_light(row_index, column_index, DummyLightDriver(offline=True))
                    else:
                        # Otherwise, we will create a new ESPMegaLightDriver
                        driver = ESPMegaLightDriver(controller, light["pwm_id"])
                        # We will then assign the driver to the light
                        self.assign_physical_light(row_index, column_index, driver)
                elif driver_type == "homeassistant":
                    # If the driver is homeassistant, we will create a new HomeAssistantLightDriver
                    # We will utilize the HomeAssistantMultiServer to manage the connections to the servers
                    ha_client = self.ha_server_bank.get_ha_client(light["api_url"], light["api_key"])
                    driver = HomeAssistantLightDriver(ha_client, light["entity_id"])
                    # We will then assign the driver to the light
                    self.assign_physical_light(row_index, column_index, driver)
    def read_light_map_from_file(self, filename: str):
        try:
            with open(filename, "r") as file:
                light_map = json.load(file)
            self.read_light_map(light_map)
        except FileNotFoundError:
            raise FileNotFoundError("The light map file does not exist.")
    def initialize_light_map(self, light_map):
        self.light_map = light_map
        self.rows = len(light_map)
        self.columns = len(light_map[0])
        self.lights = [None] * self.rows * self.columns


    @staticmethod
    def _validate_light_map(light_map):
        # This function should validate the light map

        # Check if the light map is empty
        if len(light_map) == 0:
            raise ValueError("Light map cannot be empty.")
        for row in light_map:
            UniversalLightGrid._validate_row(row, light_map[0])

    @staticmethod
    def _validate_row(row, reference_row):
        for column in row:
            UniversalLightGrid._validate_column(column)
    @staticmethod
    def _validate_column(column):
        # This function should validate the column
        pass