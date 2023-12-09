from espmega_lightshow.scripting import UserScript
import math
class CustomUserScript(UserScript):
    def draw_frame(self, current_time: float):
        # This function is called every frame
        for row in range(self.rows):
            for column in range(self.columns):
                # Calculate a value based on the current time and the position of the light
                value = math.sin(current_time + column / self.columns)
                
                # Determine the state of the light based on the calculated value
                state = value > 0
                
                # Set the state of the light at row, column
                self.set_tile_state(row, column, state)