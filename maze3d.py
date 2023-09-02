import tkinter as tk
import tkinter.messagebox as tkmb
from maze import Maze
from entities import Entity
from player import Player


class Colors:
    GREY1 = "#24142c"
    GREY2 = "#392946"
    GREY3 = "#5b537d"
    GREY4 = "#928fb8"
    BROWN1 = "#100726"
    BROWN2 = "#25082c"
    BROWN3 = "#3d1132"
    BROWN4 = "#73263d"


class Maze3d:
    def __init__(self):
        self.maze_width = 21
        self.maze_width_input = None
        self.maze_height = 21
        self.maze_height_input = None
        self.maze = None
        self.player = None

        self.window = None
        self.canvas: tk.Canvas = None
        self.canvas_width = 640
        self.canvas_height = 480
        self.message = None

        self.asking = False

    def main(self):
        self.update()
        self.window.mainloop()

    def update(self):
        if self.maze is None:
            self.setup_maze()
        self.maze.update()
        if self.window is None:
            self.setup_window()
        self.window_update()
        self.canvas_update()
        if self.maze.done:
            if not self.asking:
                self.asking = True
                time_passed = self.maze.get_time_passed()
                time_str = "%2d:%02d" % (int(time_passed / 60), time_passed % 60)
                play_again = tkmb.askyesno("Play again?",(
                    "Congratulations!  "
                    "You finished in %s.  "
                    "Would you like to play again?"
                ) % (time_str))
                if play_again:
                    self.maze = None
                    self.update()
                else:
                    self.window.destroy()
        else:
            # If we're not done, queue up an update in 1 second
            self.window.after(1000, lambda: self.update())

    def setup_maze(self):
        if self.maze_width_input is not None:
            self.maze_width = int(self.maze_width_input.get())
        if self.maze_width < 11:
            self.maze_width = 11
        if self.maze_height_input is not None:
            self.maze_height = int(self.maze_height_input.get())
        if self.maze_height < 11:
            self.maze_height = 11
        self.maze = Maze(self.maze_width, self.maze_height)
        self.maze.generate()
        if self.player is None:
            self.player = Player(0, 0)
        self.maze.add_entity(self.player)
        self.update()

    def setup_window(self):
        self.window = tk.Tk()
        self.window.title("Maze 3D")
        self.window.configure(bg="#444444")

        canvas_frame = tk.Frame(self.window, padx=8, pady=8, bg="#444444")
        canvas_frame.grid(row=0, column=0)
        self.canvas = tk.Canvas(canvas_frame,
                                width=self.canvas_width, height=self.canvas_height,
                                borderwidth=0, highlightthickness=0,
                                bg="#FFFFFF")
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Configure>", lambda e: self.canvas_configure(e))

        statue_frame = tk.Frame(self.window, padx=8, pady=8, bg="#333333")
        statue_frame.grid(row=0, column=1)

        self.message = tk.Label(statue_frame, text=self.maze.message, wraplength=300, justify="left", bg="#333333", fg="white")
        self.message.grid(row=0, column=0)

        controls_frame = tk.Frame(statue_frame, bg="#333333")
        controls_frame.grid(row=1, column=0)

        tk.Button(controls_frame, text="Forward", width=6, command=self.input_forward).grid(row=0, column=1)
        self.window.bind("w", lambda e: self.input_forward())
        self.window.bind("<Up>", lambda e: self.input_forward())
        tk.Button(controls_frame, text="Backward", width=6, command=self.input_backward).grid(row=2, column=1)
        self.window.bind("s", lambda e: self.input_backward())
        self.window.bind("<Down>", lambda e: self.input_backward())
        tk.Button(controls_frame, text="Turn Left", width=6, command=self.input_turn_left).grid(row=1, column=0)
        self.window.bind("a", lambda e: self.input_turn_left())
        self.window.bind("<Left>", lambda e: self.input_turn_left())
        tk.Button(controls_frame, text="Turn Right", width=6, command=self.input_turn_right).grid(row=1, column=2)
        self.window.bind("d", lambda e: self.input_turn_right())
        self.window.bind("<Right>", lambda e: self.input_turn_right())

        help = (
            "Search through the maze to find your way out!\n"
            "Use the controls above or the keyboard.\n"
            "[W|A|S|D] or Arrow keys to turn and move.\n"
        )
        tk.Label(statue_frame, text=help, wraplength=300, justify="left", bg="#333333", fg="white").grid(row=2, column=0)

        tk.Button(statue_frame, text="Quit", width=6, command=self.window.destroy).grid(row=3, column=0)
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        tk.Label(statue_frame, text="\nConfigure Maze:", wraplength=300, justify="left", bg="#333333", fg="white").grid(row=4, column=0)
        generate_frame = tk.Frame(statue_frame, bg="#333333")
        generate_frame.grid(row=5, column=0)
        self.maze_width_input = tk.StringVar()
        self.maze_width_input.set(str(self.maze_width))
        self.maze_height_input = tk.StringVar()
        self.maze_height_input.set(str(self.maze_height))
        tk.Entry(generate_frame, textvariable=self.maze_width_input, width=6, justify="right").grid(row=0, column=0)
        tk.Label(generate_frame, text=" x ", justify="center", bg="#333333", fg="white").grid(row=0, column=1)
        tk.Entry(generate_frame, textvariable=self.maze_height_input, width=6, justify="left").grid(row=0, column=2)
        tk.Button(statue_frame, text="Generate", width=6, command=lambda: self.setup_maze()).grid(row=6, column=0)

    def window_update(self):
        time_passed = self.maze.get_time_passed()
        self.message.config(text=self.maze.message + "\nTime: %2d:%02d" % (int(time_passed / 60), time_passed % 60))

    def canvas_configure(self, e):
        self.canvas_width = e.width
        self.canvas_height = e.height

    def canvas_update(self):
        # Find the center and steps for drawing walls
        width = self.canvas_width
        height = self.canvas_height
        center_x = int(width / 2)
        center_y = int(height / 2)
        step_x = float(width) / 6
        step_y = float(height) / 6
        last_x = width - 1
        last_y = height - 1
        xs = []
        ys = []
        for slice in range(7):
            xs.append(int(step_x * slice))
            ys.append(int(step_y * slice))
        xs[6] = last_x
        ys[6] = last_y


        # Clear the canvas
        self.canvas.delete("all")

        # Fill the background / floor and ceilings
        ceiling_colors = [Colors.BROWN4, Colors.BROWN3, Colors.BROWN2, Colors.BROWN1]
        self.canvas.create_rectangle(0, 0, width, height, width=0, outline="", fill=ceiling_colors[3])
        self.canvas.create_oval(0 - 128, center_y + 16, width + 128, height * 2, width=0, outline="", fill=ceiling_colors[2])
        self.canvas.create_oval(0 - 128, -height, width + 128, center_y - 16, width=0, outline="", fill=ceiling_colors[2])
        self.canvas.create_oval(0 - 64, center_y + 64, width + 64, height * 2, width=0, outline="", fill=ceiling_colors[1])
        self.canvas.create_oval(0 - 64, -height, width + 64, center_y - 64, width=0, outline="", fill=ceiling_colors[1])
        self.canvas.create_oval(0 - 32, center_y + 160, width + 32, height * 2, width=0, outline="", fill=ceiling_colors[0])
        self.canvas.create_oval(0 - 32, -height, width + 32, center_y - 160, width=0, outline="", fill=ceiling_colors[0])

        # Capture the current player's view
        view = self.player.get_view()

        # print("[%s][%s][%s]" % (str(view[2][0]), str(view[2][1]), str(view[2][2])))
        # print("[%s][%s][%s]" % (str(view[1][0]), str(view[1][1]), str(view[1][2])))
        # print("[%s][%s][%s]" % (str(view[0][0]), str(view[0][1]), str(view[0][2])))

        # Wall drawing functions
        wall_colors = [Colors.GREY4, Colors.GREY3, Colors.GREY2, Colors.GREY1]

        def draw_wall_left(depth):
            self.canvas.create_polygon(
                xs[depth + 0], ys[depth + 0],
                xs[depth + 1], ys[depth + 1],
                xs[depth + 1], ys[5 - depth],
                xs[depth + 0], ys[6 - depth],
                outline=wall_colors[3], fill=wall_colors[depth + 1])
            self.canvas.create_rectangle(
                0, ys[depth + 0],
                xs[depth + 0], ys[6 - depth],
                outline=wall_colors[3], fill=wall_colors[depth])

        def draw_wall_center(depth):
            self.canvas.create_rectangle(
                xs[depth + 0], ys[depth + 0],
                xs[6 - depth], ys[6 - depth],
                outline=wall_colors[3], fill=wall_colors[depth])

        def draw_wall_right(depth):
            self.canvas.create_polygon(
                xs[6 - depth], ys[depth + 0],
                xs[5 - depth], ys[depth + 1],
                xs[5 - depth], ys[5 - depth],
                xs[6 - depth], ys[6 - depth],
                outline=wall_colors[3], fill=wall_colors[depth + 1])
            self.canvas.create_rectangle(
                xs[6 - depth], ys[depth + 0],
                last_x, ys[6 - depth],
                outline=wall_colors[3], fill=wall_colors[depth])

        def draw_entity_left(depth, entity: Entity):
            x1 = float(xs[depth + 0])
            x2 = float(xs[depth + 1])
            scale_x = x2 - x1
            center_x = x1 + int(scale_x / 2)
            y11 = float(ys[depth + 0])
            y12 = float(ys[6 - depth])
            scale_y1 = y12 - y11
            center_y = y11 + int(scale_y1 / 2)
            y21 = float(ys[depth + 1])
            y22 = float(ys[5 - depth])
            scale_y2 = y22 - y21
            scale_y_change = (scale_y2 - scale_y1) / 1
            for polygon in entity.get_polygons():
                vertices = []
                for (x, y) in polygon["vertices"]:
                    y = int(y * (scale_y1 + scale_y_change * (x + 0.5))) + center_y
                    x = int(x * scale_x) + center_x
                    vertices.append(x)
                    vertices.append(y)
                self.canvas.create_polygon(*vertices, outline=wall_colors[3], fill=polygon["color"])

        def draw_entity_center(depth, entity: Entity):
            x1 = float(xs[depth + 0])
            x2 = float(xs[6 - depth])
            scale_x = x2 - x1
            y1 = float(ys[depth + 0])
            y2 = float(ys[6 - depth])
            scale_y = y2 - y1

            for polygon in entity.get_polygons():
                vertices = []
                for (x, y) in polygon["vertices"]:
                    x = int(x * scale_x) + center_x
                    y = int(y * scale_y) + center_y
                    vertices.append(x)
                    vertices.append(y)
                self.canvas.create_polygon(*vertices, outline=wall_colors[3], fill=polygon["color"])

        def draw_entity_right(depth, entity: Entity):
            x1 = float(xs[5 - depth])
            x2 = float(xs[6 - depth])
            scale_x = x2 - x1
            center_x = x1 + int(scale_x / 2)
            y11 = float(ys[depth + 0])
            y12 = float(ys[6 - depth])
            scale_y1 = y12 - y11
            center_y = y11 + int(scale_y1 / 2)
            y21 = float(ys[depth + 1])
            y22 = float(ys[5 - depth])
            scale_y2 = y22 - y21
            scale_y_change = (scale_y2 - scale_y1) / 1
            for polygon in entity.get_polygons():
                vertices = []
                for (x, y) in polygon["vertices"]:
                    y = int(y * (scale_y2 - scale_y_change * (x + 0.5))) + center_y
                    x = int(x * scale_x) + center_x
                    vertices.append(x)
                    vertices.append(y)
                self.canvas.create_polygon(*vertices, outline=wall_colors[3], fill=polygon["color"])

        # Draw from depth 2 to 0
        for depth in range(2, -1, -1):
            # Left
            if view[depth][0] == True:
                draw_wall_left(depth)
            elif isinstance(view[depth][0], Entity):
                draw_entity_left(depth, view[depth][0])
            # Right
            if view[depth][2] == True:
                draw_wall_right(depth)
            elif isinstance(view[depth][2], Entity):
                draw_entity_right(depth, view[depth][2])
            # Center
            if view[depth][1] == True:
                draw_wall_center(depth)
            elif isinstance(view[depth][1], Entity):
                draw_entity_center(depth, view[depth][1])

    def input_turn_left(self):
        self.player.turn(True)
        self.update()

    def input_turn_right(self):
        self.player.turn(False)
        self.update()

    def input_forward(self):
        self.player.move(True)
        self.update()

    def input_backward(self):
        self.player.move(False)
        self.update()


if __name__ == '__main__':
    maze3d = Maze3d()
    maze3d.main()
