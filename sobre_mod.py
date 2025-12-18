import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import time

# --- IMPORTAÇÃO DO MENU PRINCIPAL ---
from menu_jogo_mod import menu_jogo_mod

# --- CONFIGURAÇÕES DE TEMA ---
BG_COLOR = "#0D0D0D"
BG_FILENAME = "fundomenu1.png"
TEXT_COLOR = "#FFFFFF"
FONT_MAIN = ("Courier New", 16, "bold")
FONT_SMALL = ("Courier New", 13)

# --- DIMENSÕES ORIGINAIS DO FUNDO ---
BG_ORIGINAL_W = 700
BG_ORIGINAL_H = 675

def get_base_dir():
    try:
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()

BASE_DIR = get_base_dir()

def load_image(filename):
    filepath = os.path.join(BASE_DIR, filename)
    try:
        img = Image.open(filepath).convert("RGBA")
        print(f"Sucesso ao carregar: {filename}")
        return img
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filename}' não encontrado em: {BASE_DIR}")
        return Image.new("RGB", (BG_ORIGINAL_W, BG_ORIGINAL_H), "#1a1a1a")

# ===============================================================
#                    SOBRE (INTERFACE)
# ===============================================================
def mostrar_sobre(user=None):
    from menu_mod import menu_mod
    """Mostra informações sobre o jogo com animação e fundo."""
    root = tk.Tk()
    root.title("Sobre - A Jornada de Nervalia")
    root.configure(bg=BG_COLOR)
    root.state("zoomed")
    root.resizable(True, True)
    canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    bg_image = load_image(BG_FILENAME)
    bg_tk = None

    # --- TEXTOS SOBRE O JOGO ---
    textos = [
        "📖 SOBRE O JOGO – A Jornada de Nervalia",
        "",
        "Desenvolvido por:",
        "  👨‍💻 Alexandre Neves — Programação, História e Mecânicas",
        "  🎨 Ksenia Leoniuk — Design, Pixel Art e Estilo Visual",
        "",
        "Este projecto foi realizado na escola:",
        "  Escola Secundária Dr. Francisco Fernandes Lopes, Olhão",
        "",
        "O trabalho foi proposto pela professora Liliana, na disciplina de Algoritmos.",
        "",
        "Sobre o jogo:",
        "  Um cavaleiro embarca numa aventura épica para resgatar a princesa Seya, capturada por um ogre.",
        "  Ao longo do caminho, enfrentarás desafios, fazer escolhas, ganharás ou perderás HP, XP, moedas e itens.",
        "  As tuas decisões moldarão o destino do herói e da princesa.",
        "",
        "Que comece a tua jornada em Nervalia!",
        "",
        "───────────────────────────────────────────────",
        "Pressiona ENTER para voltar ao menu principal..."
    ]

    # --- ANIMAÇÃO DE TEXTO ---
    def desenhar_sobre():
        nonlocal bg_tk
        canvas.delete("all")
        win_w, win_h = root.winfo_width(), root.winfo_height()

        # Fundo redimensionado proporcional
        scale = min(win_w / BG_ORIGINAL_W, win_h / BG_ORIGINAL_H)
        new_w, new_h = int(BG_ORIGINAL_W * scale), int(BG_ORIGINAL_H * scale)
        bg_tk = ImageTk.PhotoImage(bg_image.resize((new_w, new_h), Image.NEAREST))
        canvas.bg_ref = bg_tk
        canvas.create_image(win_w // 2, win_h // 2, image=bg_tk, anchor="center")

        # Container invisível para centralizar texto
        text_y = win_h // 6  # subindo mais para caber na tela
        text_spacing = 35 * scale
        delay = 500  # ms entre linhas

        def mostrar_linha(i):
            if i >= len(textos):
                return
            texto = textos[i]
            fonte = FONT_MAIN if i == 0 else FONT_SMALL
            canvas.create_text(win_w // 2, text_y + i * text_spacing,
                               text=texto, fill=TEXT_COLOR,
                               font=fonte, anchor="n")
            root.after(delay, lambda: mostrar_linha(i + 1))

        mostrar_linha(0)

    # --- SAIR DO SOBRE ---
    def voltar_menu(event=None):
        root.destroy()
        menu_mod()

    root.bind("<Return>", voltar_menu)
    root.bind("<Escape>", voltar_menu)

    root.after(200, desenhar_sobre)
    root.mainloop()


# ===============================================================
# TESTE DIRETO
# ===============================================================
if __name__ == "__main__":
    mostrar_sobre("JogadorTeste")
