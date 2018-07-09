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
        # Initialise Coordinate Mapping for Chess Board
        ranks = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        files = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}

        # Coordinate Mapping
        coord_keys = ["".join(item)[::-1] for item in list(itertools.product(files, ranks))]
        coord_vals = list(itertools.product(files.values(), ranks.values()))

        # White on bottom
        if orientation == 0:
            self.coords = dict(zip(coord_keys, coord_vals))
        # Black on bottom
        else:
            self.coords = dict(zip(coord_keys, coord_vals[::-1]))

        self.coords_rev = {v: k for k, v in self.coords.items()}

        canvas_width = self.columns * size
        canvas_height = self.rows * size

        # Draw Chessboard
        self.canvas = tk.Canvas(self, highlightthickness=0, width=canvas_width, height=canvas_height)
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

        # Draw Coordinate System
        text_colour = self.colour2
        offset_x = 4
        offset_y = 8

        for col, rank in enumerate(list(ranks.keys())):
            x = col * self.size + offset_x
            y = self.rows * self.size - offset_y
            text_colour = self.colour1 if text_colour == self.colour2 else self.colour2
            self.rank_labels.append(self.canvas.create_text(x, y, fill=text_colour, text=rank))

        text_colour = self.colour2
        for row, file in enumerate(list(files.keys())[::-1]):
            x = self.columns * self.size - offset_x
            y = row * self.size + offset_y
            text_colour = self.colour1 if text_colour == self.colour2 else self.colour2
            self.file_labels.append(self.canvas.create_text(x, y, fill=text_colour, text=file))


        self.initialise_pieces()
        # Event Handlers

        # Click Square
        # self.canvas.bind("<Button-1>", self.click)
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

    def click(self, event):
        curr_col = int(event.x / self.size)
        curr_row = 7 - int(event.y / self.size)
        print(curr_col)
        print(curr_row)
        for x in self.squares:
            print(x)
            lbl = tk.Label

        # self.highlight_square

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
                    self.add_piece(name=item + str(self.piece_count[item] + 1), kind=item, image=self.piece_images[item], row=row, column=col)
                col += 1
if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(False, False)
    game = chess.Board()
    board = ChessBoard(parent=root, game=game)
    board.initialise_pieces()
    root.mainloop()