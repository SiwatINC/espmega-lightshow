from espmega_lightshow.scripting import UserScript
class CustomUserScript (UserScript):
    def draw_frame(self, current_time: float):
        # This function is called every frame
        # You can use self.rows and self.columns to get the number of rows and columns
        # You can use self.set_tile_state(row, column, state) to set the state of a light at row, column
        # You can use self.get_tile_state(row, column) to get the state of a light at row, column
        # You can use current_time to get the current time elapsed in seconds
        # You can use self.frame_count to get the number of frames that have passed

        # Calculate the offset based on the current time
        offset = self.frame_count % 2

        for row in range(self.rows):
            for column in range(self.columns):
                # Calculate the state based on the row, column, and offset
                state = (row + column + offset) % 2 == 0

                self.set_tile_state(row, column, state)
        pass