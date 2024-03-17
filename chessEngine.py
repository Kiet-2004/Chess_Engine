import pygame

class game_state():
    def __init__(self):
        # Game board
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        
        # Function list for getting possible move from any piece type
        self.get_move = {
            "Q": self.queen_move,
            "K": self.king_move,
            "R": self.rook_move,
            "p": self.pawn_move,
            "B": self.bishop_move,
            "N": self.knight_move
        }
        
        # Store the current turn: w = white, b = black
        self.turn = "w"
        
        # Store the move log (for many purposes like castling, en passant...)
        self.move_log = []
        
        # Store the current king location for checkmate, pin checking
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        
        # To check whether the king is checked, other pieces are being pinned by a check
        self.in_check = False
        self.pins = []
        self.checks = []
        
        # EN PASSANT
        self.en_passant = [False, (-1, -1), (-1, -1)]
        
        # For pawn promotion
        self.pawn_promotion = [False, (-1, -1)] 
        
        # For castling (kinda tricky ngl)
        self.black_queen_rook_moved = False
        self.black_king_rook_moved = False
        self.black_king_moved = False
        
        self.white_queen_rook_moved = False
        self.white_king_rook_moved = False
        self.white_king_moved = False
    
    # This function get every valid move
    def get_valid_move(self):
        # Storing valid moves
        moves = []
        
        # To check checking, pinning
        self.in_check, self.pins, self.checks = self.check_for_pins_or_check()
        
        # Get the king location
        if self.turn == "w":
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        
        # If the king is checked
        if self.in_check:
            
            # Lazy to explain step by step but basically it get every possible move first,
            # then remove moves that are invalid due to king is checked or pieces are pinned
            if len(self.checks) == 1:
                moves = self.get_possible_move()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
            
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != "K":
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.king_move(king_row, king_col, moves)
        else:
            moves = self.get_possible_move()        
            
        return moves
    
    # Get possible move from each type of pieces    
    def get_possible_move(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                current_turn = self.board[row][col][0]
                if (current_turn == self.turn):
                    piece = self.board[row][col][1]
                    self.get_move[piece](row, col, moves)   
        return moves
    
        """_This is description of how to generate possible from each pieces_
        1. First check if the piece is pinned or not
        2. Remove the piece from pin list for other pieces check
        3. Generate every possible move: pawn(forward 1, capture diagonally 1, en passant 1),
        rook (horizontal and vertical), bishop (diagonal), knight (L), queen = rook + bishop, 
        king (one cell to 8 surrounding cells or castle)
        4. If the after move, the king are still safe without being checked, then that move is valid,
        even if it is still pinned or can be captured
        """
    
    # Get every pawn possible move
    def pawn_move(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.turn == "w":
            if row - 1 >= 0:
                if self.board[row - 1][col] == "--":
                    if not piece_pinned or pin_direction == (-1, 0):
                        moves.append(Move((row, col), (row - 1, col), self.board))
                        if row == 6 and self.board[row - 2][col] == "--":
                            moves.append(Move((row, col), (row - 2, col), self.board))
                if col - 1 >= 0:
                    if self.board[row - 1][col - 1][0] == 'b' or (self.en_passant[0] and (row - 1, col - 1) == self.en_passant[1]):
                        if not piece_pinned or pin_direction == (-1, -1):
                            moves.append(Move((row, col), (row - 1, col - 1), self.board))
                if col + 1 < len(self.board[row]):
                    if self.board[row - 1][col + 1][0] == 'b' or (self.en_passant[0] and (row - 1, col + 1) == self.en_passant[1]):
                        if not piece_pinned or pin_direction == (-1, 1):
                            moves.append(Move((row, col), (row - 1, col + 1), self.board))
                    
        elif self.turn == "b":
            if row + 1 < len(self.board):
                if not piece_pinned or pin_direction == (1, 0):
                    if self.board[row + 1][col] == "--":
                        moves.append(Move((row, col), (row + 1, col), self.board))
                        if row == 1 and self.board[row + 2][col] == "--":
                            moves.append(Move((row, col), (row + 2, col), self.board))
                if col - 1 >= 0:
                    if not piece_pinned or pin_direction == (1, -1):
                        if self.board[row + 1][col - 1][0] == 'w' or (self.en_passant[0] and (row + 1, col - 1) == self.en_passant[1]):
                            moves.append(Move((row, col), (row + 1, col - 1), self.board))
                if col + 1 < len(self.board[row]):
                    if not piece_pinned or pin_direction == (1, 1):
                        if self.board[row + 1][col + 1][0] == 'w' or (self.en_passant[0] and (row + 1, col + 1) == self.en_passant[1]):
                            moves.append(Move((row, col), (row + 1, col + 1), self.board))
    
    # Get every rook possible move
    def rook_move(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction =  (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
            
        direction = ((-1, 0), (0, -1), (1, 0), (0, 1))
        opponent = "b" if self.turn == "w" else "w"
        for d in direction:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row and end_row < 8 and 0 <= end_col and end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == opponent:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    # Get every bishop possible move
    def bishop_move(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction =  (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break         
        direction = ((-1, 1), (-1, -1), (1, 1), (1, -1))
        opponent = "b" if self.turn == "w" else "w"
        for d in direction:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row and end_row < 8 and 0 <= end_col and end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == opponent:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    # Get every knight possible move
    def knight_move(self, row, col, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
            
        direction = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, 1), (2, -1), (1, 2), (1, -2))
        ally = "w" if self.turn == "w" else "b"
        for d in direction:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row and end_row < 8 and 0 <= end_col and end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
    
    # Queen move (it's just rook and bishop btw)
    def queen_move(self, row, col, moves):
        self.rook_move(row, col, moves)
        self.bishop_move(row, col, moves)
    
    # Get every King move
    def king_move(self, row, col, moves):
        direction = ((0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))
        ally = "w" if self.turn == "w" else "b"
        for d in direction:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row and end_row < 8 and 0 <= end_col and end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    if ally == "w":
                        self.white_king_location = (end_row, end_col)
                    else: 
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_or_check()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally == "w":
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)
                    if self.check_castling_king_side(row, col):
                        moves.append(Move((row, col), (row, col + 2), self.board))
                    if self.check_castling_queen_side(row, col):
                        moves.append(Move((row, col), (row, col - 2), self.board))
        
        """_Algorithm to check for pins and checks_

        1. First get every possible pinned pieces: they are pieces that stand alone with KING
        in a row, a column or a diagonal (don't count opponent)
        For example:
        wK . . wB . . . . (wB is possibly pinned in a row)
        .
        .
        wR (wR and wB here are not pinned as they are not alone with the king in the column)
        wB 
        
        2. Check from every directions if there are any rook, queen (vertical, horizontal) and 
        queen, bishop (diagonal). If between the opponent and the KING, there is possible pinned piece,
        then that piece is pinned and will be added to pin_list
        
        3. If there isn't any possible pinned piece, then the KING is being checked
        
        4. The Knight is special because of L movement so we will check Knight check by L move starting
        from the KING. Remind that Knight check cannot be stopped by any pieces (only capture the knight or run the king)
        """
    
    # Checking if the king is checked or other pieces are pinned or not
    def check_for_pins_or_check(self):
        pins = []
        checks = []
        in_check = False
        
        if self.turn == "w":
            opponent = "b"
            ally = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            opponent = "w"
            ally = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            d = directions[i]
            possible_pins = ()
            for j in range(1, 8):
                end_row = start_row + d[0] * j
                end_col = start_col + d[1] * j
                if 0 <= end_row and end_row < 8 and 0 <= end_col and end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally and end_piece[1] != "K":
                        if possible_pins == ():
                            possible_pins = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == opponent:
                        type_piece = end_piece[1]
                        if (0 <= i and i <= 3 and type_piece == "R") or \
                           (4 <= i and i <= 7 and type_piece == "B") or \
                           (j == 1 and type_piece == "p" and ((opponent == "w" and 6 <= i <= 7) or (opponent == "b" and 4 <= i <= 5))) or \
                           (type_piece == "Q") or (j == 1 and type_piece == "K"):
                            if possible_pins == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pins)
                                break
                        else:
                            break 
                else:
                    break
                        
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, 1), (2, -1), (1, 2), (1, -2))
        for d in directions:
            end_row = start_row + d[0]
            end_col = start_col + d[1]
            if 0 <= end_row and end_row < 8 and 0 <= end_col and end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == opponent and end_piece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_col, d[0], d[1]))
        
        return in_check, pins, checks
    
    # Check if we can make EN PASSANT move or not
    def check_en_passant(self):
        # If the previous move is pawn and they make 2-cell move, then it en passant
        piece_type = self.move_log[-1].get_chess_notation()[1]
        start_row = self.move_log[-1].rank_to_row[self.move_log[-1].get_chess_notation()[3]]
        start_col = self.move_log[-1].file_to_col[self.move_log[-1].get_chess_notation()[2]]
        end_row = self.move_log[-1].rank_to_row[self.move_log[-1].get_chess_notation()[5]]
        end_col = self.move_log[-1].file_to_col[self.move_log[-1].get_chess_notation()[4]]
        if piece_type == "p" and ((start_row == 6 and end_row == 4) or (start_row == 1 and end_row == 3)):
            # Store the en passant captured location, captured pawn location
            self.en_passant = [True, ((start_row + end_row) // 2, start_col), (end_row, end_col)]
    
    def en_passant_move(self):
        if self.en_passant[0]:
            # If there is en passant move
            piece_type = self.move_log[-1].get_chess_notation()[:2]
            end_row = self.move_log[-1].rank_to_row[self.move_log[-1].get_chess_notation()[5]]
            end_col = self.move_log[-1].file_to_col[self.move_log[-1].get_chess_notation()[4]]
            if piece_type[1] == "p" and (end_row, end_col) == self.en_passant[1]:
                self.board[self.en_passant[2][0]][self.en_passant[2][1]] = "--"
                
            # Even if the player didn't capture en passant, we still change it to false as en passant only last 1 turn
            self.en_passant = (False, (-1, -1), (-1, -1))
    
    # Check if we can promote our pawn or not
    def check_promotion(self):
        # Promotion is easy as we just need to check if the pawn move to the last row
        piece_type = self.move_log[-1].get_chess_notation()[1]
        end_row = self.move_log[-1].rank_to_row[self.move_log[-1].get_chess_notation()[5]]
        end_col = self.move_log[-1].file_to_col[self.move_log[-1].get_chess_notation()[4]]
        if piece_type == "p" and (end_row == 7 or end_row == 0):
            self.pawn_promotion = [True, (end_row, end_col)]
    
        """_Castlling rule_

        We cannot castle if there is one of the following conditions:
        
        1. The King is being checked
        2. After castle, the King will be checked
        3. The King or the Rook was moved before
        4. Every cells from the King to the castle location must not be checked by other piece
        
        The fourth rule is kinda hard to understand so here is the visual example
        wK .. .. .. wR
        .. .. .. .. ..
        .. bQ .. .. ..
        
        (here the white king cannot castle because the black queen is seeing one of the cell that the king will
        move through during castle) ~ Rules I read from WIKI  
        """
    
    #Apply those rules to check the castle from queen side and king side
     
    # Check if we can castle queen side    
    def check_castling_queen_side(self, row, col):
        if self.turn == "w":
            if self.white_king_moved or self.white_queen_rook_moved:
                return False
            in_check, trash, trash = self.check_for_pins_or_check()
            if in_check:
                return False
            for i in range(1, 3):
                self.white_king_location = (row, col - i)
                in_check, trash, trash = self.check_for_pins_or_check()
                if self.board[row][col - i] != "--" or in_check:
                    self.white_king_location = (row, col)
                    return False
            self.white_king_location = (row, col)
            return True
            
        if self.turn == "b":
            if self.black_king_moved or self.black_queen_rook_moved:
                return False
            in_check, trash, trash = self.check_for_pins_or_check()
            if in_check:
                return False
            for i in range(1, 3):
                self.black_king_location = (row, col - i)
                in_check, trash, trash = self.check_for_pins_or_check()
                if self.board[row][col - i] != "--" or in_check:
                    self.black_king_location = (row, col)
                    return False
            self.black_king_location = (row, col)
            return True
     
    # Check if we can castle king side    
    def check_castling_king_side(self, row, col):
        if self.turn == "w":
            if self.white_king_moved or self.white_king_rook_moved:
                return False
            in_check, trash, trash = self.check_for_pins_or_check()
            if in_check:
                return False
            for i in range(1, 3):
                self.white_king_location = (row, col + i)
                in_check, trash, trash = self.check_for_pins_or_check()
                if self.board[row][col + i] != "--" or in_check:
                    self.white_king_location = (row, col)
                    return False
            self.white_king_location = (row, col)
            return True
            
        if self.turn == "b":
            if self.black_king_moved or self.black_king_rook_moved:
                return False
            in_check, trash, trash = self.check_for_pins_or_check()
            if in_check:
                return False
            for i in range(1, 3):
                self.black_king_location = (row, col + i)
                in_check, trash, trash = self.check_for_pins_or_check()
                if self.board[row][col + i] != "--" or in_check:
                    self.black_king_location = (row, col)
                    return False
            self.black_king_location = (row, col)
            return True
    
    # Make the castle move
    def castling_move(self):
        piece_type = self.move_log[-1].get_chess_notation()[:2]
        start_col = self.move_log[-1].file_to_col[self.move_log[-1].get_chess_notation()[2]]
        end_col = self.move_log[-1].file_to_col[self.move_log[-1].get_chess_notation()[4]]
                
        if piece_type == "wK" and start_col == 4 and end_col == 6:
            self.board[7][7] = "--"
            self.board[7][5] = "wR"
            self.white_king_rook_moved = True
                
        if piece_type == "wK" and start_col == 4 and end_col == 2:
            self.board[7][0] = "--"
            self.board[7][3] = "wR"
            self.white_queen_rook_moved = True
                
        if piece_type == "bK" and start_col == 4 and end_col == 6:
            self.board[0][7] = "--"
            self.board[0][5] = "bR"
            self.black_king_rook_moved = True
                
        if piece_type == "bK" and start_col == 4 and end_col == 2:
            self.board[0][0] = "--"
            self.board[0][3] = "bR"
            self.black_queen_rook_moved = True
    
    # To make a move, store the move into the move_log and other checking for castling stuff        
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        piece_type = self.move_log[-1].get_chess_notation()[:2]
        if piece_type == "bK" and not self.black_king_moved:
            self.black_king_moved = True
        if piece_type == "wK" and not self.white_king_moved:
            self.white_king_moved = True
        start_col = self.move_log[-1].file_to_col[self.move_log[-1].get_chess_notation()[2]]
        if piece_type == "wR" and start_col == 0 and not self.white_queen_rook_moved:
            self.white_queen_rook_moved = True
        if piece_type == "wR" and start_col == 7 and not self.white_king_rook_moved:
            self.white_king_rook_moved = True
        if piece_type == "bR" and start_col == 0 and not self.black_queen_rook_moved:
            self.black_queen_rook_moved = True
        if piece_type == "bR" and start_col == 7 and not self.black_king_rook_moved:
            self.black_king_rook_moved = True
        
        self.turn = "w" if self.turn == "b" else "b"


# This class to define a move, including (start_row, start_col), (end_row, end_col)      
class Move():
    rank_to_row = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    row_to_rank = {value: key for key, value in rank_to_row.items()}
    
    file_to_col = {"h": 7, "g": 6, "f": 5, "e": 4, "d": 3, "c": 2, "b": 1, "a": 0}
    col_to_file = {value: key for key, value in file_to_col.items()}
    
    def __init__(self, start_square, end_square, board):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    
    # overriding equality     
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    
    # To get chess notation to store in move_log
    def get_chess_notation(self):
        return self.piece_moved + self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
        
    def get_rank_file(self, row, col):
        return self.col_to_file[col] + self.row_to_rank[row]
