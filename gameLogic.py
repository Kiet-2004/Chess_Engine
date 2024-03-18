import pygame as pg
import chessEngine

# BASIC SETUP FOR GAME
WIDTH = HEIGHT = 512
DIMENSION = 8
SIZE = HEIGHT // DIMENSION
FPS = 60
IMAGES = {}
CLICK_COOLDOWN = False

# To load the piece images
def load_image():
    pieces_list = ["bB", "bK", "bN", "bp", "bQ", "bR", "wB", "wK", "wN", "wp", "wQ", "wR"]
    for piece in pieces_list:
        IMAGES[piece] = pg.transform.scale(pg.image.load("assets/" + piece + ".png"), (SIZE, SIZE))

# Draw the current game state     
def draw_game_state(screen, game_state, selected_square, valid_move):
    draw_board(screen, selected_square, game_state, valid_move)
    draw_pieces(screen, game_state.board)

# Draw the board, including drawing selected cells and possible move for the selected piece
def draw_board(screen, selected_square, game_state, valid_move):
    colors = [pg.Color("white"), pg.Color("light green")]
    selected_color =[pg.Color("dark gray"), pg.Color("dark green")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            pg.draw.rect(screen, color, pg.Rect(col * SIZE, row * SIZE, SIZE, SIZE)) 
    if len(selected_square) == 2:
        row = selected_square[0]
        col = selected_square[1]  
        piece_color = game_state.board[row][col][0]
        piece_type = game_state.board[row][col][1]
        if piece_color == game_state.turn:
            color = selected_color[(row + col) % 2]
            pg.draw.rect(screen, color, pg.Rect(col * SIZE, row * SIZE, SIZE, SIZE))
            possible_move = []
            game_state.get_move[piece_type](row, col, possible_move)
            for index in possible_move:
                if index in valid_move:
                    possible_move_color = selected_color[(index.end_row + index.end_col) % 2]
                    pg.draw.rect(screen, possible_move_color, pg.Rect(index.end_col * SIZE, index.end_row * SIZE, SIZE, SIZE))

# Draw the piece
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], pg.Rect(col * SIZE, row * SIZE, SIZE, SIZE))

# Draw the promotion GUI            
def draw_promotion_state(screen, game_state):
    row = game_state.pawn_promotion[1][0]
    col = game_state.pawn_promotion[1][1]
    white_piece_type = {
        0: "wQ",
        1: "wR",
        2: "wB",
        3: "wN"
    }
    black_piece_type = {
        0: "bQ",
        1: "bR",
        2: "bB",
        3: "bN"
    }
    piece_selected = []
    clock = pg.time.Clock()
    # game_state.board[row][col] = game_state.board[row][col][0] + "Q"
    while True:
        if row == 0:
            for i in range(4):
                pg.draw.rect(screen, "purple", pg.Rect(col * SIZE, (row + i) * SIZE, SIZE, SIZE))
                screen.blit(IMAGES[white_piece_type[i]], pg.Rect(col * SIZE, (row + i) * SIZE, SIZE, SIZE))
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN:
                        location = pg.mouse.get_pos()
                        c = location[0] // SIZE
                        r = location[1] // SIZE
                        if ((row == 0 and 0 <= r <= 3)) and c == col:
                            piece_selected.append(white_piece_type[r])
        
        elif row == 7:
            for i in range(4):
                pg.draw.rect(screen, "purple", pg.Rect(col * SIZE, (row - i) * SIZE, SIZE, SIZE))
                screen.blit(IMAGES[black_piece_type[i]], pg.Rect(col * SIZE, (row - i) * SIZE, SIZE, SIZE))
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN:
                        location = pg.mouse.get_pos()
                        c = location[0] // SIZE
                        r = location[1] // SIZE
                        if (7 >= r >= 4 and row == 7) and c == col:
                            piece_selected.append(black_piece_type[7 - r])
            
        if len(piece_selected) > 0:
            game_state.board[row][col] = piece_selected[0]
            break
        clock.tick(FPS)
        pg.display.flip()

# MAIN FUNCTION           
def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    game_state = chessEngine.game_state()
    load_image()
    
    # For selecting cell and push the valid selected cell into buffer 
    selected_square = []
    selected_buffer = []
    
    # Load every possible move at first for opening
    valid_move = game_state.get_valid_move()
    
    # For checking if the move is made or not
    move_made = False
    
    # For running the game
    game_running = True
    
    # MAIN GAME
    while game_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False
            elif event.type == pg.MOUSEBUTTONUP:
                # Get the location of the mouse for selecting pieces
                location = pg.mouse.get_pos()
                col = location[0] // SIZE
                row = location[1] // SIZE
                piece_type = game_state.board[row][col][0]
                
                # If the selected piece is the same color as the player turn or there is already a cell in buffer
                if piece_type == game_state.turn or len(selected_buffer) == 1:
                    # If selected cell is the same cell in the buffer, then clear the buffer
                    if selected_square == (row, col):
                        selected_square = []
                        selected_buffer = []
                        
                    # Else push into the buffer
                    else:
                        selected_square = [row, col]
                        selected_buffer.append(selected_square)
                        
                    # If there are two cells in the buffer
                    if len(selected_buffer) == 2:
                        move = chessEngine.Move(selected_buffer[0], selected_buffer[1], game_state.board)
                        
                        # If the move is valid
                        if move in valid_move:
                            
                            # Make the move
                            game_state.make_move(move)
                            move_made = True
                            
                        # Clear buffer anyway
                        selected_square = []
                        selected_buffer = []
        
        # If the move is made    
        if move_made:
            # Relocate the location of KING
            for row in range(len(game_state.board)):
                for col in range(len(game_state.board[row])):
                    if game_state.board[row][col] == "bK":
                        game_state.black_king_location = (row, col)
                    if game_state.board[row][col] == "wK":
                        game_state.white_king_location = (row, col)
            
            # For checking castle move, en passant move or promotion move
            game_state.castling_move()
            game_state.en_passant_move()        
            game_state.check_promotion()
            if game_state.pawn_promotion[0]:
                draw_promotion_state(screen, game_state)
                game_state.pawn_promotion = [False, (-1, -1)]
                
            game_state.check_en_passant()
            
            # Get all the valid move after the move was made
            valid_move = game_state.get_valid_move()
            move_made = False
            
            # For checking endgame
            game_running = not game_state.checking_endgame(valid_move)
            print(game_state.move_log[-1].get_chess_notation() + ": " + str(game_state.piece_count))
        
        # Draw the game
        draw_game_state(screen, game_state, selected_square, valid_move)
        clock.tick(FPS)
        pg.display.flip()
