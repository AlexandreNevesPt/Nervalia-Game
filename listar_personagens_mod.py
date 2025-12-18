import csv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

CHAR_FILE = "characters.csv"

def listar_personagens(user):
    """Lista todas as personagens de um jogador específico com interface Tkinter"""
    personagens = []

    # --- Ler personagens ---
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['level'] = int(row.get('level', 0))
                    row['hp'] = int(row.get('hp', 0))
                    row['xp'] = int(row.get('xp', 0))
                    row['coins'] = int(row.get('coins', 0))
                    inv = row.get('inventory', '')
                    row['inventory'] = inv.split(',') if inv else []
                    personagens.append(row)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo: {e}")

    # --- Filtrar apenas personagens do jogador ---
    user_chars = [p for p in personagens if p['owner'] == user]

    # --- Cria janela ---
    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675
    root = tk.Tk()
    root.title(f"Personagens de {user}")
    root.configure(bg="black")
    root.resizable(False, False)

    # --- Maximiza a janela automaticamente ---
    root.state("zoomed")

    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- Fundo ---
    try:
        from Jogar_cena_mod import load_image  # import local para evitar circular import
        fundo_img = load_image("fundomenu1", is_background=True)
        fundo_img = fundo_img.resize((BG_ORIGINAL_W, BG_ORIGINAL_H), Image.NEAREST)
        fundo_tk = ImageTk.PhotoImage(fundo_img)
        # centraliza o fundo
        canvas.create_image(root.winfo_screenwidth()//2, root.winfo_screenheight()//2,
                            image=fundo_tk, anchor="center")
        canvas.fundo_ref = fundo_tk  # mantém referência para não ser coletado pelo garbage collector
    except Exception:
        pass  # se falhar, apenas mantém fundo preto

    # --- Título ---
    canvas.create_text(root.winfo_screenwidth()//2, 50, text=f"Personagens de {user}",
                       fill="white", font=("Comic Sans MS", 18, "bold"))

    # --- Lista personagens ---
    btn_y_start = 120
    btn_height = 50
    spacing = 10
    btn_refs = []

    if not user_chars:
        tk.Label(canvas, text="Nenhuma personagem encontrada.", fg="white", bg="black",
                 font=("Comic Sans MS", 14)).place(x=root.winfo_screenwidth()//2, y=btn_y_start, anchor="n")
    else:
        for i, p in enumerate(user_chars):
            txt = f"{p['name']} (Lvl {p['level']} | HP {p['hp']} | XP {p['xp']} | Moedas {p['coins']})"
            btn = tk.Button(root, text=txt, font=("Comic Sans MS", 14),
                            width=40, bg="#222", fg="white")
            canvas.create_window(root.winfo_screenwidth()//2, btn_y_start + i*(btn_height+spacing),
                                 window=btn, height=btn_height)
            btn_refs.append(btn)

    # --- Botão voltar ---
    def voltar_menu():
        root.destroy()
        from menu_mod import menu_mod  # import local para evitar circular import
        menu_mod()  # sem parâmetros, ajusta de acordo com a sua função menu_mod

    btn_voltar = tk.Button(root, text="Voltar ao Menu", font=("Comic Sans MS", 14),
                           width=20, bg="#555", fg="white", command=voltar_menu)
    canvas.create_window(root.winfo_screenwidth()//2, root.winfo_screenheight() - 60, window=btn_voltar, height=40)

    root.mainloop()
