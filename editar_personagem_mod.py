import csv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

CHAR_FILE = "characters.csv"

def editar_personagem(user):
    """Editar uma personagem do jogador com interface Tkinter"""

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
                    row['inventory'] = row.get('inventory', '').split(',') if row.get('inventory') else []
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
        messagebox.showinfo("Info", "Nenhuma personagem encontrada para edição.")
        from menu_mod import menu_mod
        menu_mod()
        return

    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675

    # --- Criar janela ---
    root = tk.Tk()
    root.title("Editar Personagem")
    root.configure(bg="black")
    root.state("zoomed")  # maximiza
    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- Fundo ---
    try:
        from Jogar_cena_mod import load_image
        fundo_img = load_image("fundomenu1", is_background=True)
        fundo_img = fundo_img.resize((BG_ORIGINAL_W, BG_ORIGINAL_H), Image.NEAREST)
        fundo_tk = ImageTk.PhotoImage(fundo_img)
        canvas.create_image(root.winfo_screenwidth()//2, root.winfo_screenheight()//2,
                            image=fundo_tk, anchor="center")
        canvas.fundo_ref = fundo_tk
    except Exception:
        pass

    # --- Título ---
    canvas.create_text(root.winfo_screenwidth()//2, 50, text="=== Editar Personagem ===",
                       fill="white", font=("Comic Sans MS", 18, "bold"))

    # --- Seleção de personagem ---
    canvas.create_text(root.winfo_screenwidth()//2, 100, text="Escolha a personagem para editar:",
                       fill="white", font=("Comic Sans MS", 14))

    btn_y_start = 140
    btn_height = 40
    spacing = 10
    btn_refs = []

    personagem_selecionada = {'data': None}

    def selecionar(p):
        personagem_selecionada['data'] = p
        for entry in entries.values():
            entry.delete(0, tk.END)
        entries['level'].insert(0, p['level'])
        entries['hp'].insert(0, p['hp'])
        entries['xp'].insert(0, p['xp'])
        entries['coins'].insert(0, p['coins'])
        entries['inventory'].insert(0, ", ".join(p['inventory']))

    for i, p in enumerate(user_chars):
        txt = f"{p['name']} (ID: {p['id']})"
        btn = tk.Button(root, text=txt, font=("Comic Sans MS", 12),
                        width=30, bg="#222", fg="white", command=lambda p=p: selecionar(p))
        canvas.create_window(root.winfo_screenwidth()//2, btn_y_start + i*(btn_height+spacing),
                             window=btn, height=btn_height)
        btn_refs.append(btn)

    # --- Campos de edição ---
    campos = ['level', 'hp', 'xp', 'coins', 'inventory']
    entries = {}
    y_start = btn_y_start + len(user_chars)*(btn_height+spacing) + 20

    for i, campo in enumerate(campos):
        tk.Label(canvas, text=campo.capitalize()+":", fg="white", bg="black",
                 font=("Comic Sans MS", 12)).place(x=root.winfo_screenwidth()//2-100, y=y_start + i*40)
        entry = tk.Entry(root, font=("Comic Sans MS", 12), width=30)
        entry.place(x=root.winfo_screenwidth()//2+50, y=y_start + i*40)
        entries[campo] = entry

    # --- Botões ---
    def salvar():
        p = personagem_selecionada['data']
        if not p:
            messagebox.showwarning("Aviso", "Selecione uma personagem primeiro!")
            return
        try:
            p['level'] = int(entries['level'].get())
            p['hp'] = int(entries['hp'].get())
            p['xp'] = int(entries['xp'].get())
            p['coins'] = int(entries['coins'].get())
            p['inventory'] = [item.strip() for item in entries['inventory'].get().split(',') if item.strip()]
        except ValueError:
            messagebox.showerror("Erro", "Level, HP, XP e Coins devem ser números!")
            return

        for i, row in enumerate(personagens):
            if row['id'] == p['id'] and row['owner'] == user:
                personagens[i] = p
                break

        try:
            with open(CHAR_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["id", "name", "level", "hp", "xp", "coins", "inventory", "owner"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in personagens:
                    row_copy = row.copy()
                    row_copy['inventory'] = ",".join(row_copy['inventory'])
                    writer.writerow(row_copy)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}")
            return

        messagebox.showinfo("Sucesso", f"Personagem '{p['name']}' atualizada com sucesso!")
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_salvar = tk.Button(root, text="Salvar Alterações", font=("Comic Sans MS", 14),
                           width=20, bg="#555", fg="white", command=salvar)
    canvas.create_window(root.winfo_screenwidth()//2, y_start + len(campos)*40 + 20, window=btn_salvar, height=40)

    def voltar():
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_voltar = tk.Button(root, text="Voltar ao Menu", font=("Comic Sans MS", 14),
                           width=20, bg="#555", fg="white", command=voltar)
    canvas.create_window(root.winfo_screenwidth()//2, y_start + len(campos)*40 + 70, window=btn_voltar, height=40)

    root.mainloop()
