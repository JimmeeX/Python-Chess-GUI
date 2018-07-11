#%%
from PIL import Image, ImageTk
import chess
import tkinter as tk
import itertools

class ChessBoard(tk.Frame):
    def __init__(self, parent, game, orientation=0, size=64, colour1="#F0D9B5", colour2="#B58863"):
        super().__init__(parent)
        self.grid()
        self.configure(background="black")

        self.selected = None
        self.selected_piece = None
        self.highlighted = None

        self.parent=parent
        self.game=game
        self.orientation = orientation

        self.rank_labels = []
        self.file_labels = []

        self.rows = 8
        self.columns = 8
        self.size = size
        self.colour1 = colour1
        self.colour2 = colour2
        self.pieces = {}
        self.piece_images = {}
        self.piece_count = {
            'b': 0,
            'k': 0,
            'n': 0,
            'p': 0,
            'q': 0,
            'r': 0,
            'B': 0,
            'K': 0,
            'N': 0,
            'P': 0,
            'Q': 0,
            'R': 0
        }

        self.initialise_images()
        # Initialise GUI

        # Menu
        self.menubar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="New Game          ", command=self.new, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Load Game", command=self.load, accelerator="Ctrl+L")
        self.file_menu.add_command(label="Save Game", command=self.save, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Quit Game", command=self.quit, accelerator="Ctrl+Q")
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.view_menu.add_command(label="Flip Board        ", command=self.flip, accelerator="Ctrl+F")
        self.menubar.add_cascade(label="View", menu=self.view_menu)


        self.parent.config(menu=self.menubar)

        # Draw Chessboard
        self.canvas = tk.Canvas(self, highlightthickness=0, width=self.columns * size, height=self.rows * size)
        self.canvas.grid(columnspan=8, rowspan=8)

        # Draw Alternating Colours on Canvas
        colour = self.colour2
        self.squares = []
        for row in range(self.rows):
            colour = self.colour1 if colour == self.colour2 else self.colour2
            for col in range(self.columns):
                x1 = col * self.size
                y1 = row * self.size
                x2 = x1 + self.size
                y2 = y1 + self.size

                # print(self.coords_rev[(row, col)])

                self.squares.append(self.canvas.create_rectangle(x1, y1, x2, y2, outline="", fill=colour, tags="square"))
                colour = self.colour1 if colour == self.colour2 else self.colour2

        self.initialise_coords()

        self.initialise_pieces()
        # Event Handlers

        # Click Square
        self.canvas.bind("<Button-1>", self.click)
        self.parent.bind("<Control-f>", self.flip)
        self.parent.bind("<Control-q>", self.quit)

    def process_image(self, path):
        img = Image.open(path).convert("RGBA")
        img = img.resize((64, 64), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def initialise_images(self):
        self.piece_images["b"] = self.process_image("images/alpha/bB.png")
        self.piece_images["k"] = self.process_image("images/alpha/bK.png")
        self.piece_images["n"] = self.process_image("images/alpha/bN.png")
        self.piece_images["p"] = self.process_image("images/alpha/bP.png")
        self.piece_images["q"] = self.process_image("images/alpha/bQ.png")
        self.piece_images["r"] = self.process_image("images/alpha/bR.png")
        self.piece_images["B"] = self.process_image("images/alpha/wB.png")
        self.piece_images["K"] = self.process_image("images/alpha/wK.png")
        self.piece_images["N"] = self.process_image("images/alpha/wN.png")
        self.piece_images["P"] = self.process_image("images/alpha/wP.png")
        self.piece_images["Q"] = self.process_image("images/alpha/wQ.png")
        self.piece_images["R"] = self.process_image("images/alpha/wR.png")

    def swap_coords(self):
        self.ranks = {k: 7 - v for k, v in self.ranks.items()}
        self.files = {k: 7- v for k, v in self.files.items()}
        coord_keys = ["".join(item)[::-1] for item in list(itertools.product(self.files, self.ranks))]
        coord_vals = list(itertools.product(self.files.values(), self.ranks.values()))
        self.coords = dict(zip(coord_keys, coord_vals))
        self.coords_rev = {v: k for k, v in self.coords.items()}

        for i, rank_idx in enumerate(self.rank_labels):
            idx = abs(self.orientation * 7 - i)
            self.canvas.itemconfigure(rank_idx, text=self.rank_keys[idx])
            # self.file_labels[i].setText(self.file_keys[7 - idx])

        for i, file_idx in enumerate(self.file_labels):
            idx = abs(self.orientation * 7 - i)
            self.canvas.itemconfigure(file_idx, text=self.file_keys[7 - idx])

    def initialise_coords(self):

        # Initialise Coordinate Mapping for Chess Board
        values = [abs(self.orientation * 7 - i) for i in range(8)]
        self.rank_keys = ["a", "b", "c", "d", "e", "f", "g", "h"]
        self.file_keys = ["1", "2", "3", "4", "5", "6", "7", "8"]
        self.ranks = {key: value for key, value in zip(rank_keys, values)}
        self.files = {key: value for key, value in zip(file_keys, values[::-1])}

        # Coordinate Mapping
        coord_keys = ["".join(item)[::-1] for item in list(itertools.product(self.files, self.ranks))]
        coord_vals = list(itertools.product(self.files.values(), self.ranks.values()))

        self.coords = dict(zip(coord_keys, coord_vals))
        self.coords_rev = {v: k for k, v in self.coords.items()}

        text_colour = self.colour2
        offset_x = 4
        offset_y = 8

        for col, rank in enumerate(sorted(self.ranks, key=lambda k: self.ranks[k])):
            x = col * self.size + offset_x
            y = self.rows * self.size - offset_y
            text_colour = self.colour1 if text_colour == self.colour2 else self.colour2
            self.rank_labels.append(self.canvas.create_text(x, y, fill=text_colour, text=rank))

        text_colour = self.colour2
        for row, file in enumerate(sorted(self.files, key=lambda k: self.files[k])):
            x = self.columns * self.size - offset_x
            y = row * self.size + offset_y
            text_colour = self.colour1 if text_colour == self.colour2 else self.colour2
            self.file_labels.append(self.canvas.create_text(x, y, fill=text_colour, text=file))

    def click(self, event):
        curr_col = int(event.x / self.size)
        curr_row = 7 - int(event.y / self.size)
        print(curr_col)
        print(curr_row)
        for x in self.squares:
            # print(x)
            lbl = tk.Label

        # self.highlight_square
    def new(self):
        print("NEW")

    def load(self):
        print("LOADING")

    def save(self):
        print("SAVING")

    def quit(self, event=None):
        self.parent.destroy()

    def flip(self, event=None):
        self.orientation = not self.orientation
        self.swap_coords()
        self.flip_pieces()
    # def highlight_square(self, pos):
    #     piece = self.canvas.

    def add_piece(self, name, kind, image, row=0, column=0):
        '''Add a piece to the playing board'''
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"), anchor="c")
        self.piece_count[kind] += 1
        self.place_piece(name, row, column)

    def place_piece(self, name, row, column):
        '''Place a piece at the given row/column'''

        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def initialise_pieces(self):
        raw_fen = self.game.fen()
        start_fen = raw_fen.split()[0].split('/')
        for row in range(8):
            col = 0
            for item in start_fen[row]:
                if item.isdigit():
                    col += int(item) - 1
                else:
                    if self.orientation == 0:
                        self.add_piece(name=item + str(self.piece_count[item] + 1), kind=item, image=self.piece_images[item], row=row, column=col)
                    else:
                        self.add_piece(name=item + str(self.piece_count[item] + 1), kind=item, image=self.piece_images[item], row= 7 - row, column= 7 - col)
                col += 1

    def flip_pieces(self):
        for name in list(self.pieces.keys()):
            row, col = self.pieces[name]
            self.place_piece(name, 7 - row, 7 - col)

if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(False, False)
    game = chess.Board()
    board = ChessBoard(parent=root, game=game, orientation=0)
    board.initialise_pieces()
    root.mainloop()