import csv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

CHAR_FILE = "characters.csv"

def apagar_personagem(user):
    """Apagar uma personagem do jogador com interface Tkinter"""

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
            messagebox.showerror("Erro", f"Erro ao ler arquivo {CHAR_FILE}: {e}")
            return
    else:
        messagebox.showwarning("Aviso", f"Arquivo {CHAR_FILE} não encontrado.")
        return

    # --- Filtrar personagens do usuário ---
    user_chars = [p for p in personagens if p['owner'] == user]
    if not user_chars:
        messagebox.showinfo("Info", "Nenhuma personagem encontrada para apagar.")
        return

    # --- Dimensões do fundo ---
    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675

    # --- Criar janela ---
    root = tk.Tk()
    root.title("Apagar Personagem")
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
    canvas.create_text(BG_ORIGINAL_W//2, 50, text="=== Apagar Personagem ===",
                       fill="white", font=("Comic Sans MS", 18, "bold"))
    canvas.create_text(BG_ORIGINAL_W//2, 100, text="Escolha a personagem para apagar:",
                       fill="white", font=("Comic Sans MS", 14))

    # --- Botões das personagens ---
    btn_y_start = 140
    btn_height = 40
    spacing = 10
    btn_refs = []

    def apagar(p):
        nonlocal personagens
        personagens = [x for x in personagens if not (x['id'] == p['id'] and x['owner'] == user)]
        try:
            with open(CHAR_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["id", "name", "level", "hp", "xp", "coins", "inventory", "owner"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for x in personagens:
                    row = x.copy()
                    row['inventory'] = ",".join(row['inventory']) if isinstance(row['inventory'], list) else row['inventory']
                    writer.writerow(row)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}")
            return
        messagebox.showinfo("Sucesso", f"Personagem '{p['name']}' apagada com sucesso!")
        root.destroy()

    def selecionar(p):
        resposta = messagebox.askyesno("Confirmação",
                                       f"Tem certeza que deseja apagar '{p['name']}'?")
        if resposta:
            apagar(p)

    for i, p in enumerate(user_chars):
        txt = f"{p['name']} (ID: {p['id']})"
        btn = tk.Button(root, text=txt, font=("Comic Sans MS", 12),
                        width=30, bg="#222", fg="white", command=lambda p=p: selecionar(p))
        canvas.create_window(BG_ORIGINAL_W//2, btn_y_start + i*(btn_height+spacing),
                             window=btn, height=btn_height)
        btn_refs.append(btn)

    # --- Botão voltar ---
    def voltar():
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_voltar = tk.Button(root, text="Voltar ao Menu", font=("Comic Sans MS", 14),
                           width=20, bg="#555", fg="white", command=voltar)
    canvas.create_window(BG_ORIGINAL_W//2, btn_y_start + len(user_chars)*(btn_height+spacing) + 50,
                         window=btn_voltar, height=40)

    root.mainloop()