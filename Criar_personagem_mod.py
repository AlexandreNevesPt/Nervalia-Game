import csv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

CHAR_FILE = "characters.csv"

def criar_personagem(user):
    """Cria uma nova personagem para o jogador com interface Tkinter"""

    # --- Ler personagens existentes para gerar novo ID ---
    personagens = []
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    personagens.append(row)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo {CHAR_FILE}: {e}")
            return

    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675

    # --- Criar janela ---
    root = tk.Tk()
    root.title("Criar Nova Personagem")
    root.configure(bg="black")
    root.resizable(False, False)
    root.state("zoomed")  # maximiza a janela

    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- Fundo ---
    try:
        from Jogar_cena_mod import load_image  # import local para evitar circular import
        fundo_img = load_image("fundomenu1", is_background=True)
        fundo_img = fundo_img.resize((BG_ORIGINAL_W, BG_ORIGINAL_H), Image.NEAREST)
        fundo_tk = ImageTk.PhotoImage(fundo_img)
        canvas.create_image(root.winfo_screenwidth()//2, root.winfo_screenheight()//2,
                            image=fundo_tk, anchor="center")
        canvas.fundo_ref = fundo_tk  # mantém referência
    except Exception:
        pass

    # --- Título ---
    canvas.create_text(root.winfo_screenwidth()//2, 50, text="=== Criar Nova Personagem ===",
                       fill="white", font=("Comic Sans MS", 18, "bold"))

    # --- Entrada de nome ---
    tk.Label(canvas, text="Nome da personagem:", fg="white", bg="black",
             font=("Comic Sans MS", 14)).place(x=root.winfo_screenwidth()//2, y=120, anchor="n")
    nome_entry = tk.Entry(root, font=("Comic Sans MS", 14), width=30)
    canvas.create_window(root.winfo_screenwidth()//2, 160, window=nome_entry)

    msg_label = tk.Label(canvas, text="", fg="red", bg="black", font=("Comic Sans MS", 12))
    msg_label.place(x=root.winfo_screenwidth()//2, y=190, anchor="n")

    # --- Botão criar ---
    def criar():
        nome = nome_entry.get().strip()
        if not nome:
            msg_label.config(text="Nome não pode ser vazio.")
            return
        if any(p['name'].lower() == nome.lower() and p['owner'] == user for p in personagens):
            msg_label.config(text="Já existe uma personagem com esse nome para este jogador.")
            return

        # atributos iniciais
        level = 1
        hp = 100
        xp = 0
        coins = 0
        inventory = []

        novo_id = f"C{len(personagens)+1:03d}"
        nova_personagem = {
            "id": novo_id,
            "name": nome,
            "level": level,
            "hp": hp,
            "xp": xp,
            "coins": coins,
            "inventory": ",".join(inventory),
            "owner": user
        }

        try:
            file_exists = os.path.exists(CHAR_FILE)
            with open(CHAR_FILE, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["id", "name", "level", "hp", "xp", "coins", "inventory", "owner"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(nova_personagem)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar personagem: {e}")
            return

        messagebox.showinfo("Sucesso", f"Personagem '{nome}' criada com sucesso! ID: {novo_id}")
        root.destroy()
        from menu_mod import menu_mod  # import local para evitar circular import
        menu_mod()  # volta ao menu principal

    btn_criar = tk.Button(root, text="Criar Personagem", font=("Comic Sans MS", 14),
                          width=20, bg="#555", fg="white", command=criar)
    canvas.create_window(root.winfo_screenwidth()//2, 250, window=btn_criar, height=40)

    # --- Botão voltar ---
    def voltar():
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_voltar = tk.Button(root, text="Voltar ao Menu", font=("Comic Sans MS", 14),
                           width=20, bg="#555", fg="white", command=voltar)
    canvas.create_window(root.winfo_screenwidth()//2, 310, window=btn_voltar, height=40)

    root.mainloop()
