import os
import csv
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw

from creditos_mod import mostrar_creditos
from sobre_mod import mostrar_sobre
import menu_jogo_mod  # para chamar menu_jogo_mod depois

# --- CONFIGURAÇÕES ---
BG_COLOR = "#0D0D0D"
BUTTON_PLACEHOLDER_COLOR = "#FF6347"
BG_PLACEHOLDER_COLOR = "#1a1a1a"
PLAYERS_FILE = "players.csv"

# --- BASE DIR ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# --- SISTEMA DE JOGADORES ---
def carregar_jogadores():
    jogadores = []
    try:
        with open(PLAYERS_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                jogadores.append({"id": row['id'], "name": row['name']})
    except FileNotFoundError:
        jogadores = []
    return jogadores

def salvar_jogadores(jogador):
    file_exists = os.path.exists(PLAYERS_FILE)
    with open(PLAYERS_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["id", "name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(jogador)

# --- FUNÇÃO PARA CARREGAR IMAGEM ---
def load_image(filename, is_background=False):
    filepath = os.path.join(BASE_DIR, filename)
    try:
        img = Image.open(filepath)
        return img
    except FileNotFoundError:
        color = BG_PLACEHOLDER_COLOR if is_background else BUTTON_PLACEHOLDER_COLOR
        size = (1200, 675) if is_background else (180, 45)
        placeholder = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(placeholder)
        draw.text((10, 10), f"{filename} (FALHOU)", fill="white")
        return placeholder

# --- FUNÇÃO PRINCIPAL DO MENU ---
def menu_mod():
    root = tk.Tk()
    root.title("Nervalia - Menu Principal")
    root.configure(bg=BG_COLOR)
    root.state("zoomed")
    root.resizable(True, True)
    canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- CARREGAR IMAGENS ---
    bg_original = load_image("fundonervalia.png", is_background=True)
    bg_w, bg_h = bg_original.size
    btn_jogar_img = load_image("jogarbotao.png")
    btn_sobre_img = load_image("sobrebotao.png")
    btn_creditos_img = load_image("creditosbotao.png")
    btn_sair_img = load_image("sairbotao.png") 

    BUTTON_IMAGES = {
        "jogar": btn_jogar_img,
        "sobre": btn_sobre_img,
        "creditos": btn_creditos_img,
        "sair": btn_sair_img
    }

    BUTTON_X = 4
    BUTTON_Y_START = 30
    BUTTON_HEIGHT = 9
    BUTTON_SPACING = 6
    BUTTON_ORDER = ["jogar", "sobre", "creditos", "sair"]

    # --- FUNÇÕES BOTÕES ---
    def mostrar_seletor_jogador():
        jogadores = carregar_jogadores()
        frame_jogador = tk.Frame(canvas, bg="#000000", bd=0)
        frame_jogador.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame_jogador, text="Escolha o jogador:", fg="white", bg="#000000").pack(padx=20, pady=10)

        listbox = tk.Listbox(frame_jogador)
        for j in jogadores:
            listbox.insert(tk.END, j["name"])
        listbox.pack(padx=20, pady=10)

        def criar_novo():
            nome_novo = simpledialog.askstring("Criar jogador", "Digite o nome do novo jogador:")
            if nome_novo:
                if any(j['name'].lower() == nome_novo.lower() for j in jogadores):
                    messagebox.showwarning("Aviso", "Já existe um jogador com esse nome.")
                else:
                    novo_id = f"P{len(jogadores)+1}"
                    novo_jogador = {"id": novo_id, "name": nome_novo}
                    salvar_jogadores(novo_jogador)
                    listbox.insert(tk.END, nome_novo)
                    jogadores.append(novo_jogador)

        def confirmar_jogador():
            selecionado = listbox.curselection()
            if selecionado:
                jogador = jogadores[selecionado[0]]
                frame_jogador.destroy()
                root.destroy()  # Fecha a janela Tkinter
                # Continua o jogo no terminal no menu_jogo_mod
                menu_jogo_mod.menu_jogo_mod(jogador["name"])
            else:
                messagebox.showwarning("Aviso", "Selecione um jogador.")

        tk.Button(frame_jogador, text="Criar Novo", command=criar_novo).pack(pady=5)
        tk.Button(frame_jogador, text="Confirmar", command=confirmar_jogador).pack(pady=5)

    def jogar():
        mostrar_seletor_jogador()

    def sobre():
        root.destroy()
        mostrar_sobre()

    def creditos():
        root.destroy()
        mostrar_creditos()

    def sair():
        root.destroy()

    FUNC_MAP = {
        "jogar": jogar,
        "sobre": sobre,
        "creditos": creditos,
        "sair": sair
    }

    # --- FUNÇÃO DE DESENHO ---
    def draw_scene(event=None):
        canvas.delete("all")
        win_w, win_h = root.winfo_width(), root.winfo_height()
        if win_w < 50 or win_h < 50: 
            return

        scale = min(win_w / bg_w, win_h / bg_h)
        new_w, new_h = int(bg_w*scale), int(bg_h*scale)
        bg_scaled = bg_original.resize((new_w, new_h), Image.NEAREST)
        bg_tk = ImageTk.PhotoImage(bg_scaled)
        canvas.bg_ref = bg_tk
        canvas.create_image(win_w//2, win_h//2, image=bg_tk, anchor="center")

        offset_x = (win_w - new_w)//2
        offset_y = (win_h - new_h)//2
        image_refs = []
        button_areas = []

        for i, name in enumerate(BUTTON_ORDER):
            img = BUTTON_IMAGES[name]
            w, h = img.size
            sw, sh_img = int(w*scale), int(h*scale)
            img_tk = ImageTk.PhotoImage(img.resize((sw, sh_img), Image.NEAREST))
            image_refs.append(img_tk)

            y_pos_original = BUTTON_Y_START + i*(BUTTON_HEIGHT + BUTTON_SPACING)
            final_y_hitbox = int(y_pos_original*scale) + offset_y
            padding_y_original = (h - BUTTON_HEIGHT) / 2
            padding_offset_y_scaled = int(padding_y_original * scale)
            final_x = int(BUTTON_X*scale) + offset_x
            final_y_image = final_y_hitbox - padding_offset_y_scaled

            canvas.create_image(final_x, final_y_image, image=img_tk, anchor="nw")
            h_scaled = int(BUTTON_HEIGHT*scale)
            x1, y1, x2, y2 = final_x, final_y_hitbox, final_x+sw, final_y_hitbox+h_scaled
            button_areas.append((x1, y1, x2, y2, FUNC_MAP[name]))

        canvas.image_refs = image_refs
        canvas.button_areas = button_areas

    # --- DETECÇÃO DE CLIQUE ---
    def on_click(event):
        for x1, y1, x2, y2, func in canvas.button_areas:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                func()
                break

    canvas.bind("<Button-1>", on_click)
    root.bind("<Configure>", draw_scene)
    root.after(100, draw_scene)
    root.mainloop()
   
   
   # --- CHAMAR O MENU ---
if __name__ == "__main__":
    menu_mod()

 