from espmega_lightshow.scripting import UserScript
class CustomUserScript (UserScript):
    def draw_frame(self, current_time: float):
        # This function is called every frame
        # You can use self.rows and self.columns to get the number of rows and columns
        # You can use self.set_tile_state(row, column, state) to set the state of a light at row, column
        # You can use self.get_tile_state(row, column) to get the state of a light at row, column
        # You can use current_time to get the current time elapsed in seconds
        # You can use self.frame_count to get the number of frames that have passed
        # You can use self.log(message) to log a message to the log console

        # Calculate the offset based on the current time
        offset = self.frame_count % 2

        # Log the frame count and offset
        self.log(f'Frame count: {self.frame_count}, offset: {offset}')
        

        # Log the sum of the row and column of each light plus the offset
        # Prettify the output by creating a ascii grid with x being the column and y being the row
        self.log("  "+" ".join([str(x) for x in range(self.columns)]))
        for row in range(self.rows):
            self.log(str(row)+" "+" ".join([str(row+column+offset) for column in range(self.columns)]))

        for row in range(self.rows):
            for column in range(self.columns):
                # Calculate the state based on the row, column, and offset
                state = (row + column + offset) % 2 == 0

                self.set_tile_state(row, column, state)
        pass