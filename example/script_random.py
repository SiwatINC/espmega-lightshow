import random
from espmega_lightshow.scripting import UserScript
class CustomUserScript (UserScript):
    def draw_frame(self, current_time: float):
        # This function is called every frame
        for row in range(self.rows):
            for column in range(self.columns):
                # Generate a random state for the light
                state = random.choice([True, False])
                # Set the state of the light at row, column
                self.set_tile_state(row, column, state)
