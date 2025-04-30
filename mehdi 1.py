import tkinter as tk
import random
import socket
import threading
import json
from tkinter import messagebox

class TicTacToe:
    def __init__(self):
        """Initialize the Tic Tac Toe game with all components"""
        self._setup_game_parameters()
        self._initialize_window()
        self._create_frames()
        self.window.mainloop()

    def _setup_game_parameters(self):
        """Set up game parameters and initial state"""
        self.player_options = {"X": "X", "O": "O"}
        self.curr_player = "X"
        self.player_symbol = "X"  # Default player symbol
        self.ai_symbol = "O"
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        
        # Color scheme
        self.color_blue = "#4584b6"
        self.color_yellow = "#ffde57"
        self.color_gray = "#343434"
        self.color_light_gray = "#646464"
        
        # Game state
        self.scores = {"X": 0, "O": 0, "Ties": 0}
        self.turns = 0
        self.game_over = False
        self.game_mode = None
        self.is_host = False
        self.connection = None
        self.server_socket = None
        self.ai_difficulty = "medium"

    def _initialize_window(self):
        """Initialize the main game window"""
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_frames(self):
        """Create all UI frames"""
        self._create_menu_frame()
        self._create_game_frame()
        self._create_connection_frame()
        self._create_symbol_selection_frame()

    def _create_menu_frame(self):
        """Create the main menu frame"""
        self.menu_frame = tk.Frame(self.window)
        
        tk.Label(
            self.menu_frame, 
            text="Tic Tac Toe", 
            font=("Consolas", 24), 
            pady=20
        ).pack()
        
        mode_frame = tk.Frame(self.menu_frame)
        tk.Label(
            mode_frame, 
            text="Select Game Mode:", 
            font=("Consolas", 14)
        ).pack()
        
        button_width = 20
        tk.Button(
            mode_frame, 
            text="Play vs AI", 
            font=("Consolas", 12), 
            width=button_width,
            command=lambda: self._set_game_mode("ai")
        ).pack(pady=5)
        
        tk.Button(
            mode_frame, 
            text="Host Online Game", 
            font=("Consolas", 12), 
            width=button_width,
            command=lambda: self._set_game_mode("online", True)
        ).pack(pady=5)
        
        tk.Button(
            mode_frame, 
            text="Join Online Game", 
            font=("Consolas", 12), 
            width=button_width,
            command=lambda: self._set_game_mode("online", False)
        ).pack(pady=5)
        
        # Creator credits
        tk.Label(
            mode_frame, 
            text="Created by: Mahdi & Wassim", 
            font=("Consolas", 10, "italic"), 
            fg="#888888"
        ).pack(pady=(0, 10))
        
        self._create_difficulty_frame()
        mode_frame.pack(pady=10)
        self.menu_frame.pack(fill="both", expand=True)

    def _create_symbol_selection_frame(self):
        """Create frame for player symbol selection (X/O)"""
        self.symbol_frame = tk.Frame(self.menu_frame)
        tk.Label(
            self.symbol_frame,
            text="Choose your symbol:",
            font=("Consolas", 12)
        ).pack()
        
        self.symbol_var = tk.StringVar(value="X")
        
        tk.Radiobutton(
            self.symbol_frame,
            text="X (First Player)",
            variable=self.symbol_var,
            value="X",
            font=("Consolas", 10),
            command=self._update_player_symbol
        ).pack(anchor="w")
        
        tk.Radiobutton(
            self.symbol_frame,
            text="O (Second Player)",
            variable=self.symbol_var,
            value="O",
            font=("Consolas", 10),
            command=self._update_player_symbol
        ).pack(anchor="w")
        
        self.symbol_frame.pack_forget()

    def _update_player_symbol(self):
        """Update player and AI symbols based on selection"""
        self.player_symbol = self.symbol_var.get()
        self.ai_symbol = "O" if self.player_symbol == "X" else "X"
        if self.game_mode == "ai" and self.curr_player == self.ai_symbol:
            self.window.after(500, self._ai_move)

    def _create_difficulty_frame(self):
        """Create AI difficulty selection frame"""
        self.ai_difficulty_frame = tk.Frame(self.menu_frame)
        tk.Label(
            self.ai_difficulty_frame, 
            text="Select AI Difficulty:", 
            font=("Consolas", 12)
        ).pack()
        
        difficulties = [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")]
        self.difficulty_var = tk.StringVar(value="medium")
        
        for text, mode in difficulties:
            tk.Radiobutton(
                self.ai_difficulty_frame, 
                text=text, 
                variable=self.difficulty_var,
                value=mode, 
                font=("Consolas", 10)
            ).pack(anchor="w")
        
        self.ai_difficulty_frame.pack_forget()

    def _create_game_frame(self):
        """Create the game play frame"""
        self.game_frame = tk.Frame(self.window)
        self._create_score_display()
        
        self.label = tk.Label(
            self.game_frame, 
            text="", 
            font=("Consolas", 20), 
            bg=self.color_gray, 
            fg="white"
        )
        self.label.pack(fill="x", pady=5)
        
        self._create_board()
        self._create_control_buttons()
        self.game_frame.pack_forget()

    def _create_score_display(self):
        """Create score display section"""
        self.score_frame = tk.Frame(self.game_frame)
        self.score_frame.pack(fill="x", pady=5)
        
        self.score_label = tk.Label(
            self.score_frame, 
            text="X: 0  |  O: 0  |  Ties: 0", 
            font=("Consolas", 12)
        )
        self.score_label.pack()

    def _create_board(self):
        """Create game board grid"""
        board_frame = tk.Frame(self.game_frame)
        board_frame.pack(pady=10)
        
        for row in range(3):
            for column in range(3):
                self.board[row][column] = tk.Button(
                    board_frame, 
                    text="", 
                    font=("Consolas", 30, "bold"),
                    bg=self.color_gray, 
                    fg=self.color_blue,
                    width=3, 
                    height=1,
                    command=lambda row=row, column=column: self._set_tile(row, column)
                )
                self.board[row][column].grid(row=row, column=column, padx=5, pady=5)

    def _create_control_buttons(self):
        """Create game control buttons"""
        button_frame = tk.Frame(self.game_frame)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame, 
            text="Restart Game", 
            font=("Consolas", 12), 
            width=15,
            command=self._restart_game
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame, 
            text="Main Menu", 
            font=("Consolas", 12), 
            width=15,
            command=self._return_to_menu
        ).pack(side="right", padx=5)

    def _create_connection_frame(self):
        """Create online connection setup frame"""
        self.connection_frame = tk.Frame(self.window)
        
        tk.Label(
            self.connection_frame, 
            text="Online Game Setup", 
            font=("Consolas", 16)
        ).pack(pady=10)
        
        self._create_host_frame()
        self._create_join_frame()
        
        tk.Button(
            self.connection_frame, 
            text="Back", 
            font=("Consolas", 12), 
            width=20,
            command=self._return_to_menu
        ).pack(pady=10)
        
        self.connection_frame.pack_forget()

    def _create_host_frame(self):
        """Create host game section"""
        host_frame = tk.Frame(self.connection_frame)
        tk.Label(
            host_frame, 
            text="Host Game", 
            font=("Consolas", 12)
        ).pack()
        
        self.host_ip_label = tk.Label(
            host_frame, 
            text="Your IP: " + self._get_local_ip()
        )
        self.host_ip_label.pack()
        
        tk.Button(
            host_frame, 
            text="Start Server", 
            font=("Consolas", 12), 
            width=20,
            command=self._start_server
        ).pack(pady=5)
        
        host_frame.pack(pady=5)

    def _create_join_frame(self):
        """Create join game section"""
        join_frame = tk.Frame(self.connection_frame)
        tk.Label(
            join_frame, 
            text="Join Game", 
            font=("Consolas", 12)
        ).pack()
        
        tk.Label(join_frame, text="IP Address:").pack()
        self.ip_entry = tk.Entry(join_frame, width=20)
        self.ip_entry.pack()
        
        tk.Button(
            join_frame, 
            text="Connect", 
            font=("Consolas", 12), 
            width=20,
            command=self._connect_to_server
        ).pack(pady=5)
        
        join_frame.pack(pady=5)

    def _update_score_display(self):
        """Update the score display"""
        self.score_label.config(
            text=f"X: {self.scores['X']}  |  O: {self.scores['O']}  |  Ties: {self.scores['Ties']}"
        )

    def _restart_game(self):
        """Restart the current game"""
        self.turns = 0
        self.game_over = False
        
        for row in range(3):
            for column in range(3):
                self.board[row][column].config(text="", fg=self.color_blue, bg=self.color_gray)
        
        if self.game_mode == "online":
            self.curr_player = "X" if self.is_host else "O"
        else:
            self.curr_player = self.player_symbol
        
        self.label.config(text=f"{self.curr_player}'s turn", fg="white")
        
        if self.game_mode == "ai" and self.curr_player == self.ai_symbol:
            self.window.after(500, self._ai_move)

    def _get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _on_close(self):
        """Handle window closing"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.window.destroy()

    def _set_game_mode(self, mode, is_host=None):
        """Set the game mode and initialize accordingly"""
        self.game_mode = mode
        self.is_host = is_host if is_host is not None else False
        
        if mode == "ai":
            self.menu_frame.pack_forget()
            self.symbol_frame.pack()
            self.ai_difficulty_frame.pack()
            self.game_frame.pack(fill="both", expand=True)
            self._start_new_game()
        elif mode == "online":
            self.menu_frame.pack_forget()
            self.connection_frame.pack(fill="both", expand=True)

    def _return_to_menu(self):
        """Return to main menu"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        self.game_frame.pack_forget()
        self.connection_frame.pack_forget()
        self.ai_difficulty_frame.pack_forget()
        self.symbol_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    def _start_new_game(self):
        """Start a new game session"""
        self.scores = {"X": 0, "O": 0, "Ties": 0}
        self._update_score_display()
        self._restart_game()

    def _set_tile(self, row, column):
        """Handle player move"""
        if self.game_over or self.board[row][column]["text"] != "":
            return
        
        if self.game_mode == "online":
            if ((self.is_host and self.curr_player != "X") or 
                (not self.is_host and self.curr_player != "O")):
                return
        
        self.board[row][column]["text"] = self.curr_player
        
        if self.game_mode == "online":
            self._send_move(row, column)
        
        self._switch_player()
        self._check_winner()
        
        if not self.game_over and self.game_mode == "ai" and self.curr_player == self.ai_symbol:
            self.window.after(500, self._ai_move)

    def _switch_player(self):
        """Switch to the other player"""
        self.curr_player = "O" if self.curr_player == "X" else "X"
        self.label.config(text=f"{self.curr_player}'s turn")

    def _check_winner(self):
        """Check for winner or tie"""
        self.turns += 1
        
        winner = self._check_win_conditions()
        if winner:
            self._handle_win(winner)
            return
        
        if self.turns == 9:
            self._handle_tie()

    def _check_win_conditions(self):
        """Check all possible winning conditions"""
        # Check rows
        for row in range(3):
            if (self.board[row][0]["text"] == self.board[row][1]["text"] == self.board[row][2]["text"] != ""):
                return self.board[row][0]["text"]
        
        # Check columns
        for column in range(3):
            if (self.board[0][column]["text"] == self.board[1][column]["text"] == self.board[2][column]["text"] != ""):
                return self.board[0][column]["text"]
        
        # Check diagonals
        if (self.board[0][0]["text"] == self.board[1][1]["text"] == self.board[2][2]["text"] != ""):
            return self.board[0][0]["text"]
        
        if (self.board[0][2]["text"] == self.board[1][1]["text"] == self.board[2][0]["text"] != ""):
            return self.board[0][2]["text"]
        
        return None

    def _handle_win(self, winner):
        """Handle winning condition"""
        self.scores[winner] += 1
        self._update_score_display()
        self.label.config(text=f"{winner} is the winner!", fg=self.color_yellow)
        self._highlight_winning_cells()
        self.game_over = True

    def _highlight_winning_cells(self):
        """Highlight winning cells"""
        for row in range(3):
            for col in range(3):
                if self.board[row][col]["text"] != "":
                    self.board[row][col].config(
                        fg=self.color_yellow, 
                        bg=self.color_light_gray
                    )

    def _handle_tie(self):
        """Handle tie game"""
        self.game_over = True
        self.label.config(text="Tie!", fg=self.color_yellow)
        self.scores["Ties"] += 1
        self._update_score_display()

    def _ai_move(self):
        """Execute AI move based on difficulty"""
        if self.game_over:
            return
        
        difficulty = self.difficulty_var.get()
        
        if difficulty == "easy":
            self._ai_move_random()
        elif difficulty == "medium":
            if random.random() < 0.7:
                self._ai_move_smart()
            else:
                self._ai_move_random()
        else:
            self._ai_move_smart()

    def _ai_move_random(self):
        """AI makes random move"""
        empty_spots = [
            (r, c) for r in range(3) 
            for c in range(3) 
            if self.board[r][c]["text"] == ""
        ]
        if empty_spots:
            r, c = random.choice(empty_spots)
            self.board[r][c]["text"] = self.curr_player
            self._switch_player()
            self._check_winner()

    def _ai_move_smart(self):
        """AI makes strategic move"""
        if self._try_winning_move():
            return
            
        if self._block_opponent():
            return
            
        if self.board[1][1]["text"] == "":
            self.board[1][1]["text"] = self.ai_symbol
            self._switch_player()
            self._check_winner()
            return
        
        corners = [(0,0), (0,2), (2,0), (2,2)]
        random.shuffle(corners)
        for r, c in corners:
            if self.board[r][c]["text"] == "":
                self.board[r][c]["text"] = self.ai_symbol
                self._switch_player()
                self._check_winner()
                return
        
        self._ai_move_random()

    def _try_winning_move(self):
        """Try to make winning move"""
        for r in range(3):
            for c in range(3):
                if self.board[r][c]["text"] == "":
                    self.board[r][c]["text"] = self.ai_symbol
                    if self._check_ai_winner():
                        self._switch_player()
                        self._check_winner()
                        return True
                    self.board[r][c]["text"] = ""
        return False

    def _block_opponent(self):
        """Block opponent's winning move"""
        for r in range(3):
            for c in range(3):
                if self.board[r][c]["text"] == "":
                    self.board[r][c]["text"] = self.player_symbol
                    if self._check_ai_winner():
                        self.board[r][c]["text"] = self.ai_symbol
                        self._switch_player()
                        self._check_winner()
                        return True
                    self.board[r][c]["text"] = ""
        return False

    def _check_ai_winner(self):
        """Check for winner (AI use)"""
        for r in range(3):
            if self.board[r][0]["text"] == self.board[r][1]["text"] == self.board[r][2]["text"] != "":
                return True
        
        for c in range(3):
            if self.board[0][c]["text"] == self.board[1][c]["text"] == self.board[2][c]["text"] != "":
                return True
        
        if (self.board[0][0]["text"] == self.board[1][1]["text"] == self.board[2][2]["text"] != "" or
            self.board[0][2]["text"] == self.board[1][1]["text"] == self.board[2][0]["text"] != ""):
            return True
        
        return False

    def _start_server(self):
        """Start online game server"""
        self.connection_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.label.config(text="Waiting for connection...")
        threading.Thread(target=self._run_server, daemon=True).start()

    def _run_server(self):
        """Run server socket"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 5555))
            self.server_socket.listen(1)
            
            self.connection, _ = self.server_socket.accept()
            
            self.window.after(0, lambda: self.label.config(text="Connected! X's turn"))
            self.window.after(0, self._start_new_game)
            
            threading.Thread(target=self._receive_moves, daemon=True).start()
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Error", f"Server error: {str(e)}"))
            self.window.after(0, self._return_to_menu)

    def _connect_to_server(self):
        """Connect to online game"""
        ip = self.ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Error", "Please enter an IP address")
            return
        
        self.connection_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.label.config(text="Connecting...")
        threading.Thread(target=self._connect_to_server_thread, args=(ip,), daemon=True).start()

    def _connect_to_server_thread(self, ip):
        """Handle server connection"""
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((ip, 5555))
            
            self.window.after(0, lambda: self.label.config(text="Connected! O's turn"))
            self.window.after(0, self._start_new_game)
            
            threading.Thread(target=self._receive_moves, daemon=True).start()
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Error", f"Connection failed: {str(e)}"))
            self.window.after(0, self._return_to_menu)

    def _send_move(self, row, col):
        """Send move to opponent"""
        if not self.connection:
            return
        
        try:
            move = json.dumps({"row": row, "col": col})
            self.connection.sendall(move.encode())
        except:
            messagebox.showerror("Error", "Connection lost")
            self._return_to_menu()

    def _receive_moves(self):
        """Receive moves from opponent"""
        while True:
            try:
                data = self.connection.recv(1024)
                if not data:
                    break
                
                move = json.loads(data.decode())
                self.window.after(0, lambda r=move["row"], c=move["col"]: self._process_received_move(r, c))
            except:
                break
        
        self.window.after(0, lambda: messagebox.showerror("Error", "Connection lost"))
        self.window.after(0, self._return_to_menu)

    def _process_received_move(self, row, col):
        """Process received move"""
        if self.game_over:
            return
        
        if ((self.is_host and self.curr_player == "O") or 
            (not self.is_host and self.curr_player == "X")):
            self.board[row][col]["text"] = "O" if self.is_host else "X"
            self._switch_player()
            self._check_winner()

if __name__ == "__main__":
    TicTacToe()