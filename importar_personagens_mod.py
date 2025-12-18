import csv
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

CHAR_FILE = "characters.csv"

def importar_personagens(user):
    """Importa personagens com interface gráfica Tkinter"""

    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675

    # --- Ler personagens existentes ---
    personagens = []
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['level'] = int(row.get('level',0))
                    row['hp'] = int(row.get('hp',0))
                    row['xp'] = int(row.get('xp',0))
                    row['coins'] = int(row.get('coins',0))
                    inv = row.get('inventory','')
                    row['inventory'] = inv.split(',') if inv else []
                    personagens.append(row)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo: {e}")
            return

    # --- Criar janela ---
    root = tk.Tk()
    root.title("Importar Personagens")
    root.configure(bg="#0D0D0D")
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
    canvas.create_text(BG_ORIGINAL_W//2, 50, text="=== Importar Personagens ===",
                       fill="white", font=("Comic Sans MS", 18, "bold"))

    # --- Escolher arquivo ---
    def escolher_arquivo():
        arquivo = filedialog.askopenfilename(title="Escolher arquivo", 
                                             filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
        if arquivo:
            entry_arquivo.delete(0, tk.END)
            entry_arquivo.insert(0, arquivo)

    canvas.create_text(BG_ORIGINAL_W//2 - 150, 120, text="Arquivo:", fill="white", font=("Comic Sans MS", 14), anchor="e")
    entry_arquivo = tk.Entry(root, width=40, font=("Comic Sans MS",12))
    canvas.create_window(BG_ORIGINAL_W//2 + 50, 120, window=entry_arquivo, height=30)
    btn_browse = tk.Button(root, text="Procurar", font=("Comic Sans MS",12), command=escolher_arquivo)
    canvas.create_window(BG_ORIGINAL_W//2 + 250, 120, window=btn_browse, height=30)

    # --- Botão Importar ---
    def importar():
        arquivo_origem = entry_arquivo.get().strip()
        if not arquivo_origem or not os.path.exists(arquivo_origem):
            messagebox.showwarning("Aviso", "Arquivo não encontrado!")
            return

        novas_personagens = []

        try:
            if arquivo_origem.endswith(".csv"):
                with open(arquivo_origem, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        # validar campos
                        if not all(k in row for k in ["id","name","level","hp","xp","coins","inventory","owner"]):
                            continue
                        if row['owner'] != user:
                            continue
                        row['level'] = int(row['level'])
                        row['hp'] = int(row['hp'])
                        row['xp'] = int(row['xp'])
                        row['coins'] = int(row.get('coins',0))
                        row['inventory'] = row.get('inventory','').split(',') if row.get('inventory') else []
                        novas_personagens.append(row)

            elif arquivo_origem.endswith(".txt"):
                with open(arquivo_origem,'r',encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(", ")
                        p_dict = {}
                        for part in parts:
                            if ": " not in part:
                                continue
                            k,v = part.split(": ")
                            p_dict[k.strip()] = v.strip()
                        if p_dict.get('owner') != user:
                            continue
                        p_dict['level'] = int(p_dict.get('level',1))
                        p_dict['hp'] = int(p_dict.get('hp',100))
                        p_dict['xp'] = int(p_dict.get('xp',0))
                        p_dict['coins'] = int(p_dict.get('coins',0))
                        p_dict['inventory'] = p_dict.get('inventory','').split(',') if p_dict.get('inventory') else []
                        p_dict['id'] = p_dict.get('id', f"C{len(personagens)+len(novas_personagens)+1:03d}")
                        novas_personagens.append(p_dict)
            else:
                messagebox.showerror("Erro","Formato inválido! Somente CSV ou TXT.")
                return
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo: {e}")
            return

        if not novas_personagens:
            messagebox.showinfo("Info", "Nenhuma personagem válida encontrada no arquivo.")
            return

        # --- Mesclar e salvar ---
        importadas = 0
        atualizadas = 0
        for nova in novas_personagens:
            existente = next((p for p in personagens if p['id']==nova['id'] and p['owner']==user), None)
            if existente:
                personagens = [nova if p['id']==nova['id'] and p['owner']==user else p for p in personagens]
                atualizadas += 1
            else:
                personagens.append(nova)
                importadas += 1

        try:
            with open(CHAR_FILE,'w',newline='',encoding='utf-8') as csvfile:
                fieldnames = ["id","name","level","hp","xp","coins","inventory","owner"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for p in personagens:
                    p_copy = p.copy()
                    p_copy['inventory'] = ",".join(p_copy.get('inventory',[]))
                    p_copy['coins'] = int(p_copy.get('coins',0))
                    writer.writerow(p_copy)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar personagens: {e}")
            return

        messagebox.showinfo("Sucesso", f"Importação concluída!\n{importadas} importadas, {atualizadas} atualizadas.")
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_importar = tk.Button(root, text="Importar", font=("Comic Sans MS",14), width=20, bg="#555", fg="white", command=importar)
    canvas.create_window(BG_ORIGINAL_W//2, 180, window=btn_importar, height=40)

    # --- Botão voltar ---
    def voltar():
        root.destroy()
        from menu_mod import menu_mod
        menu_mod()

    btn_voltar = tk.Button(root, text="Voltar ao Menu", font=("Comic Sans MS",14), width=20, bg="#555", fg="white", command=voltar)
    canvas.create_window(BG_ORIGINAL_W//2, 240, window=btn_voltar, height=40)

    root.mainloop()
