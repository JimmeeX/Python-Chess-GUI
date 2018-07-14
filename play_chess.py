#%%
from PIL import Image, ImageTk
from enum import IntFlag
import chess
import tkinter as tk
import itertools
#%%
class HighlightTags(IntFlag):
    SELECT = 1 # WHOLE SQUARE
    MOVE = 2 # INNER CIRCLE
    PIECE = 4 # JUST THE OUTER
    CHECK = 8 # OUTER CIRCLE
    PROMOTION = 16 # EVERYTHING IS DIFFERENT LOL
    SELECT_CHECK = SELECT | CHECK
#%%
class ChessBoard(tk.Frame):
    def __init__(self, parent, game, orientation=0, size=64, colour1="#F0D9B5", colour2="#B58863"):
        super().__init__(parent)
        self.grid()
        self.configure(background="black")

        self.selected_piece = None
        self.selected = None
        self.possible_moves = []

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
        self.piece_ids = {}
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

        self.promotion_options = []
        self.promotion_pieces = {}
        self.promotion_piece_ids = {}

        # Square Highlighting
        self.square_ids = []
        self.outer_circle_ids = []
        self.inner_circle_ids = []
        self.check_square = None
        self.highlight_map = {}

        self.move_history = []

        # Drag Drop
        self.move_flag = False
        self.move_piece = None
        self.initial_x = None
        self.initial_y = None

        self.initialise_images()
        self.initialise_coords()
        self.initialise_menu()
        self.initialise_chessboard()
        self.initialise_side_panel()
        self.initialise_rank_files()
        self.initialise_pieces()
        self.initialise_drag_drop()

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

        self.highlight_map = dict(zip(coord_keys, [0] * 64))

    def initialise_menu(self):
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

    def initialise_chessboard(self):
        # Draw Chessboard
        self.canvas = tk.Canvas(self, highlightthickness=0, width=self.columns * self.size, height=self.rows * self.size)
        self.canvas.grid(columnspan=8, rowspan=8)

        # Draw Alternating Colours on Canvas
        colour = self.colour2
        for row in range(self.rows):
            colour = self.colour1 if colour == self.colour2 else self.colour2
            for col in range(self.columns):
                x1 = col * self.size
                y1 = row * self.size
                x2 = x1 + self.size
                y2 = y1 + self.size
                r1 = 7
                r2 = 32
                self.square_ids.append(self.canvas.create_rectangle(x1, y1, x2, y2, outline="", fill=colour, tags="square"))
                self.outer_circle_ids.append(self.canvas.create_oval((x1+x2)/2-r2, (y1+y2)/2-r2, (x1+x2)/2+r2, (y1+y2)/2+r2, outline="", fill=colour, tags="outer_circle"))
                self.inner_circle_ids.append(self.canvas.create_oval((x1+x2)/2-r1, (y1+y2)/2-r1, (x1+x2)/2+r1, (y1+y2)/2+r1, outline="", fill=colour, tags="inner_circle"))
                colour = self.colour1 if colour == self.colour2 else self.colour2

    def initialise_side_panel(self):
        #TODO: MOVE HISTORY
        #TODO: PIECE CAPTURES
        #TODO: LEFT+RIGHT
        self.side_panel = tk.Frame(self, width=self.columns * self.size / 2, height= self.rows * self.size, bg="#262626")
        self.side_panel.grid(column=8, row=0, columnspan=4, rowspan=8)

        self.result_label = tk.Label(self, text="Game over: Insufficient Material 1-0", font=("Impact", 12), bg="#262626", fg="#888888", anchor="c")
        self.result_label.grid(row=0, column=8, columnspan=4)

    def initialise_rank_files(self):
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

    def initialise_drag_drop(self):
        for _, piece in self.piece_ids.items():
            self.canvas.tag_bind(piece, "<ButtonPress-1>", self.drag_select)
            self.canvas.tag_bind(piece, "<Button1-Motion>", self.drag_move)
            self.canvas.tag_bind(piece, "<ButtonRelease-1>", self.drag_release)
            # self.canvas.config(piece, cursor="hand1")

        # widget.bind("<ButtonPress-1>", self.on_start)
        # widget.bind("<B1-Motion>", self.on_drag)
        # widget.bind("<ButtonRelease-1>", self.on_drop)
        # widget.configure(cursor="hand1")
    def click(self, event):
        move_made = False
        curr_col = int(event.x / self.size)
        curr_row = int(event.y / self.size)
        curr_coord = self.coords_rev[(curr_row, curr_col)]
        square_id = self.get_square_id(curr_coord)
        curr_piece, curr_colour = self.square_contains_piece(curr_coord)

        if curr_coord in self.possible_moves:
            from_coord = self.selected
            if self.is_promotion(from_coord, self.selected_piece):
                self.show_promotion(curr_coord)
                self.highlight_squares()
                self.canvas.bind("<Button-1>", self.click_promotion)
                return
            self.make_move(curr_coord)
            self.assess_position()
            move_made = True
        self.remove_highlight()
        if curr_colour == self.game.turn and not move_made:
            self.set_highlight(curr_coord, curr_piece)
        self.highlight_squares()

    def click_promotion(self, event):
        curr_col = int(event.x / self.size)
        curr_row = int(event.y / self.size)
        curr_coord = self.coords_rev[(curr_row, curr_col)]
        promotion_pieces_rev = {v: k for k, v in self.promotion_pieces.items()}
        if curr_coord in self.promotion_options:
            promotion = promotion_pieces_rev[curr_coord][1].lower()
            to_coord = self.promotion_options[0]
            self.make_move(to_coord, promotion)
            self.assess_position()
        else:
            promotion = ""
        self.hide_promotion()
        self.remove_highlight()
        self.highlight_squares()
        self.canvas.bind("<Button-1>", self.click)

    def null(self, event):
        pass

    def remove_highlight(self):
        if self.selected is not None:
            if HighlightTags.CHECK in HighlightTags(self.highlight_map[self.selected]) and self.game.is_check():
                self.highlight_map[self.selected] -= HighlightTags.SELECT.value
            else:
                self.highlight_map[self.selected] = 0
            for coord in self.possible_moves:
                self.highlight_map[coord] = 0
        self.selected = None
        self.possible_moves = []
        self.selected_piece = None

    def set_highlight(self, coord, piece):
        """Highlights Piece and its Available Moves"""
        self.selected = coord
        self.highlight_map[coord] += HighlightTags.SELECT.value
        self.selected_piece = piece
        for possible_coords in self.get_possible_squares(coord):
            piece, colour = self.square_contains_piece(possible_coords)
            if colour is None:
                self.highlight_map[possible_coords] += HighlightTags.MOVE.value
            else:
                self.highlight_map[possible_coords] += HighlightTags.PIECE.value
            self.possible_moves.append(possible_coords)

    def highlight_squares(self):
        highlight_dict = {
            0: self.highlight_none,
            HighlightTags.SELECT.value: self.highlight_select,
            HighlightTags.MOVE.value: self.highlight_move,
            HighlightTags.PIECE.value: self.highlight_piece,
            HighlightTags.CHECK.value: self.highlight_check,
            HighlightTags.PROMOTION.value: self.highlight_promotion,
            HighlightTags.SELECT_CHECK.value: self.highlight_select_check
        }
        for coord, tag in self.highlight_map.items():
            highlight_dict[tag](coord)

    def highlight_none(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill=self.get_square_colour(coord))
        self.canvas.itemconfigure(self.get_outer_circle_id(coord), fill=self.get_square_colour(coord))
        self.canvas.itemconfigure(self.get_inner_circle_id(coord), fill=self.get_square_colour(coord))

    def highlight_select(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill="#646F40")
        self.canvas.itemconfigure(self.get_outer_circle_id(coord), fill="#646F40")
        self.canvas.itemconfigure(self.get_inner_circle_id(coord), fill="#646F40")

    def highlight_move(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill=self.get_square_colour(coord))
        self.canvas.itemconfigure(self.get_outer_circle_id(coord), fill=self.get_square_colour(coord))
        self.canvas.itemconfigure(self.get_inner_circle_id(coord), fill="#646F40")

    def highlight_piece(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill="#646F40")
        self.canvas.itemconfigure(self.get_outer_circle_id(coord), fill=self.get_square_colour(coord))
        self.canvas.itemconfigure(self.get_inner_circle_id(coord), fill=self.get_square_colour(coord))

    def highlight_check(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill=self.get_square_colour(coord))
        self.canvas.itemconfigure(self.get_outer_circle_id(coord), fill="#D33527")
        self.canvas.itemconfigure(self.get_inner_circle_id(coord), fill="#D33527")

    def highlight_promotion(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill="#45453D")
        self.canvas.itemconfigure(self.get_outer_circle_id(coord), fill="#989898")
        self.canvas.itemconfigure(self.get_inner_circle_id(coord), fill="#989898")

    def highlight_select_check(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill="#646F40")
        self.canvas.itemconfigure(self.get_outer_circle_id(coord), fill="#D33527")
        self.canvas.itemconfigure(self.get_inner_circle_id(coord), fill="#D33527")

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
        self.highlight_squares()
        self.canvas.bind("<Button-1>", self.click)

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

        # for i, coord in enumerate(self.promotion_options):
        #     row, col = self.coords[coord]
        #     self.promotion_options[i] = self.coords_rev[(7 - row, 7 - col)]

        self.remove_highlight()
        self.hide_promotion()

    def flip_pieces(self):
        for name in list(self.pieces.keys()):
            row, col = self.coords[self.pieces[name]]
            self.place_piece(name, self.coords_rev[(row, col)])

        for name in list(self.promotion_pieces.keys()):
            row, col = self.coords[self.promotion_pieces[name]]
            self.place_piece(name, self.coords_rev[(row, col)], promotion=True)

    def add_piece(self, name, kind, image, coord):
        '''Add a piece to the playing board'''
        self.piece_ids[coord] = self.canvas.create_image(0, 0, image=image, tags=(name, "piece"), anchor="c")
        self.piece_count[kind] += 1
        self.place_piece(name, coord)

    def place_piece(self, name, coord, promotion=False):
        '''Place a piece at the given row/column'''
        if promotion:
            self.promotion_pieces[name] = coord
        else:
            self.pieces[name] = coord
        row, col = self.coords[coord]
        x0 = (col * self.size) + int(self.size/2)
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
                    coord = self.coords_rev[(row, col)]
                    coord_flip = self.coords_rev[(7 - row, 7 - col)]
                    if self.orientation == 0:
                        self.add_piece(name=item + str(self.piece_count[item] + 1), kind=item, image=self.piece_images[item], coord=coord)
                    else:
                        self.add_piece(name=item + str(self.piece_count[item] + 1), kind=item, image=self.piece_images[item], coord=coord_flip)
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
        idx_list = list(self.piece_ids.values())
        for idx in idx_list:
            self.canvas.delete(idx)
        self.piece_ids = {}

    def square_contains_piece(self, coord):
        piece_coords = {k: v for v, k in self.pieces.items()}
        if coord in piece_coords:
            piece = piece_coords[coord]
            return (piece, self.piece_colour(piece))
        else:
            return (None, None)

    def piece_colour(self, piece):
        return piece[0].isupper()

    def get_square_id(self, coord):
        row, col = self.coords[coord]
        return self.square_ids[row * 8 + col]

    def get_inner_circle_id(self, coord):
        row, col = self.coords[coord]
        return self.inner_circle_ids[row * 8 + col]

    def get_outer_circle_id(self, coord):
        row, col = self.coords[coord]
        return self.outer_circle_ids[row * 8 + col]

    def get_square_colour(self, coord):
        row, col = self.coords[coord]
        colours = [self.colour1, self.colour2]
        return colours[(row + col % 2) % 2]

    def get_possible_squares(self, coord_from):
        squares = []
        valid_moves = list(self.game.legal_moves)
        for coord_to in list(self.coords.keys()):
            move = chess.Move.from_uci(coord_from + coord_to)
            move_promotion = chess.Move.from_uci(coord_from + coord_to + "q")
            if move in valid_moves or move_promotion in valid_moves:
                squares.append(coord_to)
        return squares

    def is_promotion(self, coord, piece):
        if piece[0] == "P" and coord[1] == "7":
            return True
        elif piece[0] == "p" and coord[1] == "2":
            return True
        return False

    def show_promotion(self, coord):
        row, col = self.coords[coord]
        pieces = [["q", "n", "r", "b"], ["Q", "N", "R", "B"]]
        for i in range(4):
            if row == 0:
                self.draw_promotion_piece(self.coords_rev[i, col], pieces[self.game.turn][i])
                self.highlight_map[self.coords_rev[i, col]] = HighlightTags.PROMOTION.value
                self.promotion_options.append(self.coords_rev[i, col])
            else:
                self.draw_promotion_piece(self.coords_rev[7 - i, col], pieces[self.game.turn][i])
                self.highlight_map[self.coords_rev[7 - i, col]] = HighlightTags.PROMOTION.value
                self.promotion_options.append(self.coords_rev[7 - i, col])

    def hide_promotion(self):
        for coord in self.promotion_options:
            self.highlight_map[coord] = 0
            # self.highlight_square(coord, colour=self.get_square_colour(coord))
        self.promotion_options = []
        self.promotion_pieces = {}
        idx_list = list(self.promotion_piece_ids.values())
        for idx in idx_list:
            self.canvas.delete(idx)
        self.piece_ids = {}
        # for i in range(len(self.promotion_piece_ids)):
        #     idx = self.promotion_piece_ids.pop()
        #     self.canvas.delete(idx)

    def highlight_promotion_square(self, coord):
        self.canvas.itemconfigure(self.get_square_id(coord), fill="#45453D")
        self.canvas.itemconfigure(self.get_move_square_id(coord), fill="#989898")
        self.canvas.itemconfigure(self.get_piece_square_id(coord), fill="#989898")

    def draw_promotion_piece(self, coord, piece):
        name = "=" + piece
        self.promotion_piece_ids[coord] = self.canvas.create_image(0, 0, image=self.piece_images[piece], tags=(name, "piece"), anchor="c")
        self.place_piece(name, coord, promotion=True)

    def make_move(self, coord_to, promotion=""):
        move = chess.Move.from_uci(self.selected + coord_to + promotion)
        self.game.push(move)
        self.move_history.append(move)
        self.initialise_pieces()

    def assess_position(self):
        if self.game.is_check():
            king_coord = list(self.coords.keys())[self.game.king(self.game.turn)]
            self.highlight_map[king_coord] += HighlightTags.CHECK.value
            self.check_square = king_coord
        elif self.check_square is not None:
            self.highlight_map[self.check_square] -= HighlightTags.CHECK.value
            self.check_square = None

        if self.game.is_game_over(claim_draw=True):
            string = "Game Over: "
            if self.game.is_checkmate():
                string += "Checkmate "
            elif self.game.is_stalemate():
                string += "Stalemate "
            elif self.is_insufficient_material():
                string += "Insufficient Material "
            elif self.is_seventyfive_moves():
                string += "75 Moves "
            elif self.is_fivefold_repetition():
                string += "5-fold Repetition "
            string += self.game.result()
            self.result_label.config(text=string)
            self.canvas.bind("<Button-1>", self.click)

    def drag_select(self, event):
        print(event)
        print("SELECT")

    def drag_move(self, event):
        if self.move_flag:
            print(event.x, event.y)
            new_xpos, new_ypos = event.x, event.y

            self.canvas.coords(self.move_piece, event.x, event.y)
            # self.canvas.move(self.move_piece, self.initial_x-new_xpos ,self.initial_y-new_ypos)

            # print("X: "+str(self.initial_x-new_xpos))
            # print("Y: "+str(self.initial_y-new_ypos))
        else:
            self.move_flag = True
            curr_col = int(event.x / self.size)
            curr_row = int(event.y / self.size)
            curr_coord = self.coords_rev[(curr_row, curr_col)]
            self.move_piece = self.piece_ids[curr_coord]
            self.initial_x = event.x
            self.initial_y = event.y

    def drag_release(self, event):
        self.move_flag = False
        self.move_piece = None
        self.initial_x = None
        self.initial_y = None
        print("RELEASE")

if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(False, False)
    game = chess.Board(fen="r1bqkb1r/pPp1p3/8/3pPQp1/P1nP1P2/2N5/2P3Pp/R1B1K3 w Qkq - 0 16")
    board = ChessBoard(parent=root, game=game, orientation=0)
    root.mainloop()