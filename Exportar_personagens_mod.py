import csv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

CHAR_FILE = "characters.csv"

def exportar_personagens(user):
    """Exportar personagens do jogador com interface Tkinter"""

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
        messagebox.showinfo("Info", "Nenhuma personagem encontrada para exportar.")
        from menu_mod import menu_mod
        menu_mod()
        return

    # --- Dimensões padrão ---
    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675

    # --- Criar janela ---
    root = tk.Tk()
    root.title("Exportar Personagens")
    root.configure(bg="black")
    root.geometry(f"{BG_ORIGINAL_W}x{BG_ORIGINAL_H}")
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
    canvas.create_text(BG_ORIGINAL_W//2, 50, text="=== Exportar Personagens ===",
                       fill="white", font=("Comic Sans MS", 18, "bold"))

    # --- Lista de personagens ---
    canvas.create_text(BG_ORIGINAL_W//2, 100, text="Personagens do jogador:",
                       fill="white", font=("Comic Sans MS", 14))
    y_start = 130
    spacing = 40
    for i, p in enumerate(user_chars):
        p_text = f"ID: {p['id']} | Nome: {p['name']} | Level: {p['level']} | HP: {p['hp']} | XP: {p['xp']}"
        canvas.create_text(BG_ORIGINAL_W//2, y_start + i*spacing, text=p_text,
                           fill="white", font=("Comic Sans MS", 12), justify="center")

    # --- Funções de exportação ---
    def export_csv():
        arquivo_saida = f"{user}_personagens_export.csv"
        try:
            with open(arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["id", "name", "level", "hp", "xp", "owner"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for p in user_chars:
                    writer.writerow(p)
            messagebox.showinfo("Sucesso", f"Personagens exportadas para {arquivo_saida}!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para CSV: {e}")

    def export_txt():
        arquivo_saida = f"{user}_personagens_export.txt"
        try:
            with open(arquivo_saida, 'w', encoding='utf-8') as txtfile:
                for p in user_chars:
                    txtfile.write(f"ID: {p['id']}, Nome: {p['name']}, Level: {p['level']}, HP: {p['hp']}, XP: {p['xp']}\n")
            messagebox.showinfo("Sucesso", f"Personagens exportadas para {arquivo_saida}!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para TXT: {e}")

    # --- Botões de exportação ---
    btn_csv = tk.Button(root, text="Exportar CSV", font=("Comic Sans MS", 14),
                        width=20, bg="#222", fg="white", command=export_csv)
    canvas.create_window(BG_ORIGINAL_W//2 - 100, BG_ORIGINAL_H - 100, window=btn_csv, height=40)

    btn_txt = tk.Button(root, text="Exportar TXT", font=("Comic Sans MS", 14),
                        width=20, bg="#222", fg="white", command=export_txt)
    canvas.create_window(BG_ORIGINAL_W//2 + 100, BG_ORIGINAL_H - 100, window=btn_txt, height=40)

    # --- Botão voltar ---
    def voltar():
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_voltar = tk.Button(root, text="Voltar ao Menu", font=("Comic Sans MS", 14),
                           width=20, bg="#555", fg="white", command=voltar)
    canvas.create_window(BG_ORIGINAL_W//2, BG_ORIGINAL_H - 50, window=btn_voltar, height=40)

    root.mainloop()
