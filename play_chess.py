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

        self.selected_piece = None
        self.highlighted = []

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
        self.piece_ids = []
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

        self.squares = []
        self.move_squares = []
        self.piece_squares = []
        self.promotion_highlighted = []
        self.promotion_pieces = {}
        self.promotion_piece_ids = []

        self.initialise_images()

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

        self.initialise_chessboard()
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

        for i, file_idx in enumerate(self.file_labels):
            idx = abs(self.orientation * 7 - i)
            self.canvas.itemconfigure(file_idx, text=self.file_keys[7 - idx])

        self.remove_highlight()
        self.hide_promotion()

    def initialise_chessboard(self):
        # Draw Chessboard
        self.canvas = tk.Canvas(self, highlightthickness=0, width=self.columns * self.size, height=self.rows * self.size)
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
                r1 = 7
                r2 = 32
                self.squares.append(self.canvas.create_rectangle(x1, y1, x2, y2, outline="", fill=colour, tags="square"))
                self.piece_squares.append(self.canvas.create_oval((x1+x2)/2-r2, (y1+y2)/2-r2, (x1+x2)/2+r2, (y1+y2)/2+r2, outline="", fill=colour, tags="outer_circle"))
                self.move_squares.append(self.canvas.create_oval((x1+x2)/2-r1, (y1+y2)/2-r1, (x1+x2)/2+r1, (y1+y2)/2+r1, outline="", fill=colour, tags="inner_circle"))
                colour = self.colour1 if colour == self.colour2 else self.colour2

    def initialise_coords(self):

        # Initialise Coordinate Mapping for Chess Board
        values = [abs(self.orientation * 7 - i) for i in range(8)]
        self.rank_keys = ["a", "b", "c", "d", "e", "f", "g", "h"]
        self.file_keys = ["1", "2", "3", "4", "5", "6", "7", "8"]
        self.ranks = {key: value for key, value in zip(self.rank_keys, values)}
        self.files = {key: value for key, value in zip(self.file_keys, values[::-1])}

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
        move_made = False
        curr_col = int(event.x / self.size)
        curr_row = int(event.y / self.size)
        square_id = self.get_square_id(curr_row, curr_col)
        curr_piece, curr_color = self.square_contains_piece(curr_row, curr_col)

        if (curr_row, curr_col) in self.highlighted[1:]:
            from_row, from_col = self.highlighted[0]
            promotion = ""
            if self.is_promotion(from_row, from_col, self.selected_piece):
                self.show_promotion(curr_row, curr_col)
                self.canvas.bind("<Button-1>", self.click_promotion)
                return
            self.make_move(curr_row, curr_col, promotion)
            move_made = True
        self.remove_highlight()
        if curr_color == self.game.turn and not move_made:
            self.highlight_piece(curr_row, curr_col, curr_piece)

    def click_promotion(self, event):
        curr_col = int(event.x / self.size)
        curr_row = int(event.y / self.size)
        promotion_pieces_rev = {v: k for k, v in self.promotion_pieces.items()}
        if (curr_row, curr_col) in self.promotion_highlighted:
            promotion = promotion_pieces_rev[(curr_row, curr_col)][1].lower()
            row, col = self.promotion_highlighted[0]
            self.make_move(row, col, promotion)
        else:
            promotion = ""
        self.hide_promotion()
        self.remove_highlight()
        self.canvas.bind("<Button-1>", self.click)

    def remove_highlight(self):
        for row, col in self.highlighted:
            self.highlight_square(row, col, colour=self.get_square_colour(row, col))
        self.highlighted = []
        self.selected_piece = None

    def highlight_piece(self, row, col, piece):
        """Highlights Piece and its Available Moves"""
        square_id = self.get_square_id(row, col)
        self.highlight_square(row, col, colour="#646F40")
        self.selected_piece = piece
        self.highlighted.append((row, col))
        for row_, col_ in self.get_possible_squares(row, col):
            piece, colour = self.square_contains_piece(row_, col_)
            # Move Square
            if colour is None:
                self.highlight_move_square(row_, col_, colour="#646F40")
            # Piece Square
            else:
                self.highlight_piece_square(row_, col_, colour="#646F40")
            self.highlighted.append((row_, col_))

    def highlight_square(self, row, col, colour):
        self.canvas.itemconfigure(self.get_square_id(row, col), fill=colour)
        self.canvas.itemconfigure(self.get_move_square_id(row, col), fill=colour)
        self.canvas.itemconfigure(self.get_piece_square_id(row, col), fill=colour)

    def highlight_move_square(self, row, col, colour):
        self.canvas.itemconfigure(self.get_move_square_id(row, col), fill=colour)

    def highlight_piece_square(self, row, col, colour):
        self.canvas.itemconfigure(self.get_square_id(row, col), fill=colour)

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
        self.canvas.bind("<Button-1>", self.click)

    def add_piece(self, name, kind, image, row=0, column=0):
        '''Add a piece to the playing board'''
        self.piece_ids.append(self.canvas.create_image(0, 0, image=image, tags=(name, "piece"), anchor="c"))
        self.piece_count[kind] += 1
        self.place_piece(name, row, column)

    def place_piece(self, name, row, column, promotion=False):
        '''Place a piece at the given row/column'''
        if promotion:
            self.promotion_pieces[name] = (row, column)
        else:
            self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def initialise_pieces(self):
        self.clear_pieces()
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

    def clear_pieces(self):
        self.pieces = {}
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
        for i in range(len(self.piece_ids)):
            idx = self.piece_ids.pop()
            self.canvas.delete(idx)

    def flip_pieces(self):
        for name in list(self.pieces.keys()):
            row, col = self.pieces[name]
            self.place_piece(name, 7 - row, 7 - col)

        for name in list(self.promotion_pieces.keys()):
            row, col = self.promotion_pieces[name]
            self.place_piece(name, 7 - row, 7 - col, promotion=True)
    def square_contains_piece(self, row, col):
        piece_coords = {k: v for v, k in self.pieces.items()}
        if (row, col) in piece_coords:
            piece = piece_coords[(row, col)]
            return (piece, self.piece_colour(piece))
        else:
            return (None, None)

    def piece_colour(self, piece):
        return piece[0].isupper()

    def get_square_id(self, row, col):
        return self.squares[row * 8 + col]

    def get_move_square_id(self, row, col):
        return self.move_squares[row * 8 + col]

    def get_piece_square_id(self, row, col):
        return self.piece_squares[row * 8 + col]

    def get_square_colour(self, row, col):
        colours = [self.colour1, self.colour2]
        return colours[(row + col % 2) % 2]

    def get_possible_squares(self, row, col):
        coord_from = self.coords_rev[(row, col)]
        squares = []
        valid_moves = list(self.game.legal_moves)
        for coord_to in list(self.coords.keys()):
            move = chess.Move.from_uci(coord_from + coord_to)
            move_promotion = chess.Move.from_uci(coord_from + coord_to + "q")
            if move in valid_moves or move_promotion in valid_moves:
                row, col = self.coords[coord_to]
                squares.append((row, col))
        return squares

    def is_promotion(self, row, col, piece):
        coord = self.coords_rev[(row, col)]
        if piece[0] == "P" and coord[1] == "7":
            return True
        elif piece[0] == "p" and coord[1] == "2":
            return True
        return False

    def show_promotion(self, row, col):
        pieces = [["q", "n", "r", "b"], ["Q", "N", "R", "B"]]
        for i in range(4):
            if row == 0:
                self.draw_promotion_piece(i, col, pieces[self.game.turn][i])
                self.highlight_promotion_square(i, col)
                self.promotion_highlighted.append((i, col))
            else:
                self.draw_promotion_piece(7 - i, col, pieces[self.game.turn][i])
                self.highlight_promotion_square(7 - i, col)
                self.promotion_highlighted.append((7 - i, col))

    def hide_promotion(self):
        for row, col in self.promotion_highlighted:
            self.highlight_square(row, col, colour=self.get_square_colour(row, col))
        self.promotion_highlighted = []
        self.promotion_pieces = {}
        for i in range(len(self.promotion_piece_ids)):
            idx = self.promotion_piece_ids.pop()
            self.canvas.delete(idx)

    def highlight_promotion_square(self, row, col):
        self.canvas.itemconfigure(self.get_square_id(row, col), fill="#45453D")
        self.canvas.itemconfigure(self.get_move_square_id(row, col), fill="#989898")
        self.canvas.itemconfigure(self.get_piece_square_id(row, col), fill="#989898")

    def draw_promotion_piece(self, row, col, piece):
        name = "=" + piece
        self.promotion_piece_ids.append((self.canvas.create_image(0, 0, image=self.piece_images[piece], tags=(name, "piece"), anchor="c")))
        self.place_piece(name, row, col, promotion=True)

    def make_move(self, row_to, col_to, promotion):
        selected = self.coords_rev[self.highlighted[0]]
        move = chess.Move.from_uci(selected + self.coords_rev[(row_to, col_to)] + promotion)
        self.game.push(move)
        self.initialise_pieces()

if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(False, False)
    game = chess.Board()
    board = ChessBoard(parent=root, game=game, orientation=0)
    root.mainloop()