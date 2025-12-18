import csv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

CHAR_FILE = "characters.csv"

def ver_estatisticas(user):
    """Exibe estatísticas do jogador com interface Tkinter"""

    # --- Ler personagens existentes ---
    personagens = []
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
            messagebox.showerror("Erro", f"Erro ao ler o arquivo {CHAR_FILE}: {e}")
            return
    else:
        messagebox.showwarning("Aviso", f"Arquivo {CHAR_FILE} não encontrado.")
        return

    # --- Filtrar personagens do usuário ---
    user_chars = [p for p in personagens if p['owner'] == user]
    if not user_chars:
        messagebox.showinfo("Info", "Nenhuma personagem encontrada para estatísticas.")
        return

    # --- Estatísticas automáticas ---
    total_chars = len(user_chars)
    media_xp = sum(p['xp'] for p in user_chars) / total_chars
    media_hp = sum(p['hp'] for p in user_chars) / total_chars
    personagem_mais_forte = max(user_chars, key=lambda p: p['level'])
    personagem_mais_fraco = min(user_chars, key=lambda p: p['level'])

    # --- Dimensões do fundo ---
    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675

    # --- Criar janela ---
    root = tk.Tk()
    root.title(f"Estatísticas de {user}")
    root.geometry(f"{BG_ORIGINAL_W}x{BG_ORIGINAL_H}")
    root.configure(bg="#0D0D0D")
    root.resizable(False, False)

    canvas = tk.Canvas(root, width=BG_ORIGINAL_W, height=BG_ORIGINAL_H, highlightthickness=0, bg="#0D0D0D")
    canvas.pack(fill="both", expand=True)

    # --- Fundo ---
    try:
        from Jogar_cena_mod import load_image
        fundo_img = load_image("fundomenu1", is_background=True)
        fundo_img = fundo_img.resize((BG_ORIGINAL_W, BG_ORIGINAL_H), Image.NEAREST)
        fundo_tk = ImageTk.PhotoImage(fundo_img)
        canvas.create_image(BG_ORIGINAL_W//2, BG_ORIGINAL_H//2, image=fundo_tk, anchor="center")
        canvas.fundo_ref = fundo_tk
    except Exception:
        pass

    # --- Título ---
    canvas.create_text(BG_ORIGINAL_W//2, 40, text="=== Estatísticas do Jogador ===",
                       fill="white", font=("Comic Sans MS", 18, "bold"))

    # --- Estatísticas principais ---
    stats_text = (f"Total de personagens: {total_chars}\n"
                  f"XP médio: {media_xp:.2f}\n"
                  f"HP médio: {media_hp:.2f}\n"
                  f"Personagem mais forte: {personagem_mais_forte['name']} (Level {personagem_mais_forte['level']})\n"
                  f"Personagem mais fraca: {personagem_mais_fraco['name']} (Level {personagem_mais_fraco['level']})")

    canvas.create_text(BG_ORIGINAL_W//2, 120, text=stats_text, fill="white",
                       font=("Comic Sans MS", 14), justify="center")

    # --- Listagem completa das personagens ---
    y_start = 250
    spacing = 50
    for i, p in enumerate(sorted(user_chars, key=lambda x: x['level'], reverse=True)):
        p_text = f"ID: {p['id']} | Nome: {p['name']} | Level: {p['level']} | HP: {p['hp']} | XP: {p['xp']}"
        canvas.create_text(BG_ORIGINAL_W//2, y_start + i*spacing, text=p_text, fill="white",
                           font=("Comic Sans MS", 12), justify="center")

    # --- Botão voltar ---
    def voltar():
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_voltar = tk.Button(root, text="Voltar ao Menu", font=("Comic Sans MS", 14),
                           width=20, bg="#555", fg="white", command=voltar)
    canvas.create_window(BG_ORIGINAL_W//2, BG_ORIGINAL_H - 60, window=btn_voltar, height=40)

    root.mainloop()
