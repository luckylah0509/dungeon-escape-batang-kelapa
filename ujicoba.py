

import tkinter as tk
import random

# ==============================
# BEBASLUCKY88 ARCADE
# ==============================

root = tk.Tk()
root.title("BEBASLUCKY88.COM")
root.geometry("1100x750")
root.configure(bg="#090909")
root.resizable(False, False)

GOLD = "#FFD700"
DARK = "#090909"
PANEL = "#191919"
WHITE = "#FFFFFF"
RED = "#C00025"
GREEN = "#00CC88"

score = 0
active_game = NoneaAzQWEDSX344

# ==============================
# HEADER
# ==============================

header = tk.Frame(root, bg="#111111", height=80)
header.pack(fill="x")

tk.Label(
    header,
    text="♛ BEBASLUCKY88",
    font=("Arial", 25, "bold"),
    fg=GOLD,
    bg="#111111"
).pack(side="left", padx=25, pady=20)

score_label = tk.Label(
    header,
    text="SCORE: 0",
    font=("Arial", 15, "bold"),
    fg=GOLD,
    bg="#111111"
)
score_label.pack(side="right", padx=30)

def add_score(value):
    global score
    score += value
    score_label.config(text=f"SCORE: {score}")

# ==============================
# NAVIGATION
# ==============================

nav = tk.Frame(root, bg="#242424")
nav.pack(fill="x")

content = tk.Frame(root, bg=DARK)
content.pack(fill="both", expand=True)

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

def heading(title, subtitle):
    tk.Label(
        content,
        text=title,
        font=("Arial", 27, "bold"),
        fg=GOLD,
        bg=DARK
    ).pack(pady=(35, 10))

    tk.Label(
        content,
        text=subtitle,
        font=("Arial", 11),
        fg="#BBBBBB",
        bg=DARK
    ).pack(pady=5)

def button(parent, text, command, width=20):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 13, "bold"),
        bg=GOLD,
        fg="#000000",
        activebackground="#FFF0A0",
        width=width,
        pady=10,
        relief="flat",
        cursor="hand2"
    )

# ==============================
# HOME
# ==============================

def home():

    clear_content()

    heading(
        "WELCOME TO BEBASLUCKY88",
        "THE ULTIMATE DIGITAL ARCADE EXPERIENCE"
    )

    tk.Label(
        content,
        text="🎮",
        font=("Arial", 85),
        bg=DARK,
        fg=GOLD
    ).pack(pady=15)

    tk.Label(
        content,
        text="PILIH PERMAINAN FAVORITMU",
        font=("Arial", 17, "bold"),
        fg=WHITE,
        bg=DARK
    ).pack(pady=15)

    button(
        content,
        "🎰 LUCKY SLOTS",
        lucky_slots
    ).pack(pady=8)

    button(
        content,
        "🃏 BLACKJACK 21 CHALLENGE",
        blackjack
    ).pack(pady=8)

    button(
        content,
        "🎡 ROULETTE SPINNER",
        roulette
    ).pack(pady=8)

# ==============================
# GAME 1: LUCKY SLOTS PUZZLE
# ==============================

def lucky_slots():

    clear_content()

    heading(
        "LUCKY SYMBOL MATCH",
        "Cocokkan ketiga simbol untuk menyelesaikan tantangan!"
    )

    symbols = ["💎", "👑", "🍒", "⭐", "🔔", "7️⃣"]

    frame = tk.Frame(content, bg="#292000")
    frame.pack(pady=30)

    reels = []

    for i in range(3):

        label = tk.Label(
            frame,
            text="❔",
            font=("Segoe UI Emoji", 55),
            width=3,
            height=2,
            bg="#222222",
            fg=GOLD
        )

        label.pack(side="left", padx=8, pady=8)
        reels.append(label)

    result = tk.Label(
        content,
        text="SIAPKAN DIRIMU!",
        font=("Arial", 18, "bold"),
        fg=GOLD,
        bg=DARK
    )
    result.pack(pady=10)

    spinning = [False]

    def animate(count):

        if count < 15:

            for reel in reels:
                reel.config(text=random.choice(symbols))

            root.after(100, lambda: animate(count + 1))

        else:

            final = [random.choice(symbols) for _ in range(3)]

            for i in range(3):
                reels[i].config(text=final[i])

            if final[0] == final[1] == final[2]:
                result.config(text="PERFECT MATCH! +100 SCORE", fg=GOLD)
                add_score(100)

            elif len(set(final)) == 2:
                result.config(text="NICE MATCH! +30 SCORE", fg=GREEN)
                add_score(30)

            else:
                result.config(text="COBA LAGI!", fg=WHITE)

            spinning[0] = False

    def start():

        if spinning[0]:
            return

        spinning[0] = True
        result.config(text="SYMBOLS SPINNING...", fg=GOLD)
        animate(0)

    button(content, "⚡ SPIN SYMBOLS", start, 25).pack(pady=20)

# ==============================
# GAME 2: BLACKJACK 21 CHALLENGE
# ==============================

def blackjack():

    clear_content()

    heading(
        "BLACKJACK 21 CHALLENGE",
        "Susun kartu dengan total nilai mendekati 21."
    )

    cards = []
    total = 0
    finished = [False]

    card_display = tk.Label(
        content,
        text="🂠",
        font=("Arial", 55),
        fg=GOLD,
        bg=DARK
    )
    card_display.pack(pady=15)

    total_label = tk.Label(
        content,
        text="TOTAL: 0",
        font=("Arial", 22, "bold"),
        fg=GOLD,
        bg=DARK
    )
    total_label.pack(pady=10)

    result = tk.Label(
        content,
        text="Ambil kartu untuk memulai!",
        font=("Arial", 13),
        fg=WHITE,
        bg=DARK
    )
    result.pack(pady=15)

    def draw():

        nonlocal total

        if finished[0]:
            return

        value = random.randint(2, 11)

        cards.append(value)
        total += value

        card_display.config(
            text="  ".join(str(c) for c in cards)
        )

        total_label.config(text=f"TOTAL: {total}")

        if total == 21:
            result.config(text="EXACT 21! +100 SCORE", fg=GOLD)
            add_score(100)
            finished[0] = True

        elif total > 21:
            result.config(text="LEBIH DARI 21! GAME OVER", fg=RED)
            finished[0] = True

        else:
            result.config(text="KAMU BISA AMBIL KARTU LAGI!", fg=GREEN)

    def finish():

        if finished[0] or not cards:
            return

        finished[0] = True

        if total < 21:
            result.config(
                text=f"BERHASIL BERTAHAN! +{total} SCORE",
                fg=GOLD
            )
            add_score(total)

    controls = tk.Frame(content, bg=DARK)
    controls.pack(pady=15)

    button(
        controls,
        "DRAW CARD",
        draw,
        15
    ).pack(side="left", padx=10)

    button(
        controls,
        "FINISH",
        finish,
        15
    ).pack(side="left", padx=10)

    button(
        content,
        "NEW GAME",
        blackjack,
        15
    ).pack(pady=10)

# ==============================
# GAME 3: ROULETTE SPINNER
# ==============================

def roulette():

    clear_content()

    heading(
        "ROULETTE SPINNER",
        "Putar roda warna dan lihat hasil acaknya!"
    )

    colors = [
        ("🔴", "RED"),
        ("⚫", "BLACK"),
        ("🟢", "GREEN")
    ]

    display = tk.Label(
        content,
        text="🎡",
        font=("Arial", 100),
        bg=DARK,
        fg=GOLD
    )
    display.pack(pady=20)

    result = tk.Label(
        content,
        text="RODA SIAP DIPUTAR",
        font=("Arial", 20, "bold"),
        fg=GOLD,
        bg=DARK
    )
    result.pack(pady=15)

    running = [False]

    def rotate(count=0):

        if count < 20:

            symbol, name = random.choice(colors)

            display.config(text=symbol)
            result.config(text=name)

            root.after(100, lambda: rotate(count + 1))

        else:

            symbol, name = random.choice(colors)

            display.config(text=symbol)

            result.config(
                text=f"HASIL AKHIR: {name}",
                fg=GOLD
            )

            running[0] = False

    def start():

        if running[0]:
            return

        running[0] = True
        result.config(text="RODA BERPUTAR...", fg=GOLD)
        rotate()

    button(
        content,
        "🎡 SPIN ROULETTE",
        start,
        25
    ).pack(pady=20)


# ==============================
# GAME 4: DOMINO CHALLENGE
# ==============================

def domino():

    clear_content()

    heading(
        "DOMINO CHALLENGE",
        "Main domino melawan komputer!"
    )

    # Membuat set kartu domino
    deck = [
        (a, b)
        for a in range(7)
        for b in range(a, 7)
    ]

    random.shuffle(deck)

    player_hand = deck[:7]
    computer_hand = deck[7:14]

    board = [deck[14]]

    # DISPLAY
    board_label = tk.Label(
        content,
        text="",
        font=("Arial", 25, "bold"),
        fg=GOLD,
        bg=DARK
    )
    board_label.pack(pady=20)

    status = tk.Label(
        content,
        text="Giliran kamu!",
        font=("Arial", 15, "bold"),
        fg=WHITE,
        bg=DARK
    )
    status.pack(pady=10)

    tk.Label(
        content,
        text="KARTU DOMINO KAMU",
        font=("Arial", 12, "bold"),
        fg=GOLD,
        bg=DARK
    ).pack(pady=10)

    hand_frame = tk.Frame(content, bg=DARK)
    hand_frame.pack(pady=10)

    computer_label = tk.Label(
        content,
        text=f"Kartu komputer: {len(computer_hand)}",
        font=("Arial", 12),
        fg=WHITE,
        bg=DARK
    )
    computer_label.pack(pady=10)

    game_over = [False]

    def show_board():

        board_label.config(
            text="  ".join(
                f"[{a}|{b}]" for a, b in board
            )
        )

        computer_label.config(
            text=f"Kartu komputer: {len(computer_hand)}"
        )

    def finish(message, won):

        game_over[0] = True

        status.config(
            text=message,
            fg=GOLD if won else RED
        )

        if won:
            add_score(100)

        for widget in hand_frame.winfo_children():
            widget.config(state="disabled")

    def refresh_hand():

        for widget in hand_frame.winfo_children():
            widget.destroy()

        for index, card in enumerate(player_hand):

            a, b = card

            tk.Button(
                hand_frame,
                text=f"{a} | {b}",
                font=("Arial", 15, "bold"),
                bg=GOLD,
                fg="#000000",
                width=5,
                height=2,
                command=lambda i=index: play_card(i)
            ).pack(side="left", padx=4)

    def play_card(index):

        if game_over[0]:
            return

        card = player_hand[index]

        left = board[0][0]
        right = board[-1][1]

        a, b = card

        # Cek kartu yang cocok di kiri atau kanan
        if a == right:
            board.append(card)

        elif b == right:
            board.append((b, a))

        elif b == left:
            board.insert(0, card)

        elif a == left:
            board.insert(0, (b, a))

        else:
            status.config(
                text="Kartu tidak cocok!",
                fg=RED
            )
            return

        player_hand.pop(index)

        show_board()
        refresh_hand()

        if not player_hand:
            finish("KAMU MENANG! +100 SCORE", True)
            return

        status.config(
            text="Giliran komputer...",
            fg=GOLD
        )

        root.after(800, computer_turn)

    def computer_turn():

        if game_over[0]:
            return

        left = board[0][0]
        right = board[-1][1]

        valid_card = None

        for i, card in enumerate(computer_hand):

            a, b = card

            if a == right or b == right:
                valid_card = (i, "right")
                break

            if a == left or b == left:
                valid_card = (i, "left")
                break

        if valid_card is not None:

            index, side = valid_card
            a, b = computer_hand.pop(index)

            if side == "right":

                if a == right:
                    board.append((a, b))
                else:
                    board.append((b, a))

            else:

                if b == left:
                    board.insert(0, (a, b))
                else:
                    board.insert(0, (b, a))

            show_board()

            if not computer_hand:
                finish("KOMPUTER MENANG!", False)
                return

        status.config(
            text="Giliran kamu!",
            fg=GREEN
        )

    def pass_turn():

        if game_over[0]:
            return

        left = board[0][0]
        right = board[-1][1]

        # Pass hanya jika tidak ada kartu yang cocok
        for a, b in player_hand:

            if a in (left, right) or b in (left, right):
                status.config(
                    text="Masih ada kartu yang bisa dimainkan!",
                    fg=RED
                )
                return

        status.config(
            text="Kamu melewati giliran.",
            fg=GOLD
        )

        root.after(800, computer_turn)

    show_board()
    refresh_hand()

    tk.Button(
        content,
        text="PASS TURN",
        font=("Arial", 12, "bold"),
        bg="#333333",
        fg=WHITE,
        width=18,
        command=pass_turn
    ).pack(pady=15)

    tk.Button(
        content,
        text="NEW GAME",
        font=("Arial", 12, "bold"),
        bg=GOLD,
        fg="#000000",
        width=18,
        command=domino
    ).pack(pady=5)


# ==============================
# NAV BUTTONS
# ==============================

button(nav, "HOME", home, 12).pack(side="left", padx=10, pady=10)
button(nav, "SLOTS", lucky_slots, 12).pack(side="left", padx=10, pady=10)
button(nav, "CARDS", blackjack, 12).pack(side="left", padx=10, pady=10)
button(nav, "ROULETTE", roulette, 12).pack(side="left", padx=10, pady=10)
button(nav, "DOMINO", domino, 12).pack(side="left", padx=10, pady=10)

# FOOTER


tk.Label(
    root,
    text="BEBASLUCKY88 | ARCADE GAME | FREE PLAY",
    font=("Arial", 9),
    fg="#777777",
    bg=DARK
).pack(pady=10)

home()

root.mainloop()
