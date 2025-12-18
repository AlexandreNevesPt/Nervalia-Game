import csv
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

# ------------------- ARQUIVO DE PERSONAGENS -------------------
CHAR_FILE = "characters.csv"

# ------------------- DIRETÓRIO BASE -------------------
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# ------------------- FUNÇÕES DE LEITURA E ESCRITA CSV -------------------
def carregar_personagens():
    """Carrega personagens do CSV e retorna uma lista de dicionários."""
    personagens = []
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Converte campos numéricos
                    for key in ['hp', 'xp', 'level', 'coins']:
                        try:
                            row[key] = int(row.get(key) or 0)
                        except:
                            row[key] = 0
                    # Converte inventário em lista
                    inv = row.get('inventory')
                    row['inventory'] = [i.strip() for i in inv.split(',') if i.strip()] if inv else []
                    personagens.append(row)
        except Exception as e:
            print(f"Erro ao ler {CHAR_FILE}: {e}")
    return personagens

def salvar_personagens(personagens):
    """Salva a lista de personagens de volta no CSV."""
    try:
        with open(CHAR_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["id", "name", "level", "hp", "xp", "coins", "inventory", "owner"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for p in personagens:
                p_copy = p.copy()
                p_copy["inventory"] = ",".join(p_copy.get("inventory", []))
                writer.writerow(p_copy)
    except Exception as e:
        print(f"Erro ao salvar {CHAR_FILE}: {e}")

def escolher_personagem(user):
    BG_ORIGINAL_W = 700
    BG_ORIGINAL_H = 675
    personagens = carregar_personagens()
    user_chars = [p for p in personagens if p['owner'] == user]
    if not user_chars:
        tk.messagebox.showinfo("Nenhuma personagem", "Nenhuma personagem encontrada para este jogador.")
        return None

    escolha = {'personagem': None}

    def selecionar(p):
        escolha['personagem'] = p
        root.destroy()

    root = tk.Tk()
    root.title(f"Escolher Personagem - {user}")
    root.configure(bg="#0D0D0D")
    root.state("zoomed")  # abre maximizada
    root.resizable(False, False)

    canvas = tk.Canvas(root, bg="#0D0D0D", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- Fundo na dimensão original, centralizado ---
    fundo_img = load_image("fundomenu1", is_background=True)
    fundo_tk = ImageTk.PhotoImage(fundo_img.resize((BG_ORIGINAL_W, BG_ORIGINAL_H), Image.NEAREST))
    win_w = root.winfo_screenwidth()
    win_h = root.winfo_screenheight()
    canvas.create_image(win_w//2, win_h//2, image=fundo_tk, anchor="center")
    canvas.bg_ref = fundo_tk  # evita garbage collection

    # --- Título ---
    canvas.create_text(win_w//2, 50, text=f"Escolha a personagem de {user}",
                       fill="white", font=("Comic Sans MS", 18, "bold"))

    # --- Botões ---
    btn_y_start = 120
    btn_height = 50
    spacing = 10
    btn_refs = []

    for i, p in enumerate(user_chars):
        txt = f"{p['name']} (Lvl {p['level']} | HP {p['hp']} | XP {p['xp']} | Moedas {p['coins']})"
        btn = tk.Button(root, text=txt, font=("Comic Sans MS", 14),
                        width=40, bg="#222", fg="white",
                        command=lambda p=p: selecionar(p))
        canvas.create_window(win_w//2, btn_y_start + i*(btn_height+spacing), window=btn, height=btn_height)
        btn_refs.append(btn)  # mantém referência

    root.mainloop()
    return escolha['personagem']
# ------------------- FUNÇÃO PARA CARREGAR IMAGENS -------------------
def load_image(filename, is_background=False):
    """
    Carrega imagem de arquivo.
    Se não existir, cria um placeholder com texto de erro.
    """
    filepath = os.path.join(BASE_DIR, filename + ".png")
    try:
        img = Image.open(filepath).convert("RGBA")
        return img
    except FileNotFoundError:
        size = (1280, 720) if is_background else (200, 300)
        color = (0,0,0,180) if is_background else (100,100,100,255)
        img = Image.new("RGBA", size, color)
        draw = ImageDraw.Draw(img)
        draw.text((10,10), f"{filename} (FALHOU)", fill="white")
        return img

# ------------------- FUNÇÃO PRINCIPAL DO JOGO -------------------
def jogar_cena(user):
    """Inicia a cena principal do jogo para o jogador escolhido."""
    personagem = escolher_personagem(user)
    if not personagem:
        return

    # --- CRIA JANELA ---
    root = tk.Tk()
    root.title(f"Nervalia - {personagem['name']}")
    root.state("zoomed")  # janela maximizada
    root.resizable(True, True)  # permite redimensionar

    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- CARREGAR IMAGENS ---
    fundo_original = load_image("fundomenu1", is_background=True)  # background do menu
    legenda_original = load_image("backgroundLegendas", is_background=True)  # caixa de legendas
    personagens_imgs = {
        "principal": load_image("PersonagemPrincipal"),
        "rei": load_image("ReiCogumelo"),
        "mulher": load_image("MulherCogumeloPobreComCriancas"),
        "vilao": load_image("CogumeloMau"),
        "princesa": load_image("princesa"),
        "Dragao" : load_image("Dragao"),
        "HomemMercado" : load_image("CogumeloMercado")
    }

    # --- REFERÊNCIAS PARA TKIMAGES ---
    main_img_ref = []  # para personagem principal
    npc_img_ref = []   # para NPCs

    # --- NOVO: VARIÁVEL GLOBAL PARA NPC ATUAL ---
    npc_atual = None  # inicializa sem NPC

    # --- HUD ---
    hud_text = canvas.create_text(0,0,text="",fill="yellow",font=("Comic Sans MS",16,"bold"),anchor="ne")
    def atualizar_hud():
        """Atualiza texto do HUD com HP, XP e Moedas."""
        canvas.itemconfigure(hud_text, text=f"HP: {personagem['hp']} ❤️  XP: {personagem['xp']} ⭐  Moedas: {personagem['coins']} 💰")

    # --- LEGENDAS ---
    # (NOTA: mantemos apenas uma criação de legenda_text para evitar confusão)
    legenda_text = canvas.create_text(
        0, 0,
        text="",
        fill="white",
        font=("Comic Sans MS", 22, "bold"),
        anchor="nw",
        width=500, # largura inicial, será ajustada
        tags="legenda_text"
    )

    def atualizar_legenda(texto):
        """Atualiza texto da legenda e reposiciona na parte inferior."""
        win_w, win_h = root.winfo_width(), root.winfo_height()
        canvas.coords(legenda_text, 50, win_h-320+10)
        canvas.itemconfigure(legenda_text, text=texto)

    # --- FUNÇÃO DE DELAY PARA PRINT NA LEGENDA ---
    def delay_print(texto, index=0, callback=None):
        if index < len(texto):
            current = canvas.itemcget(legenda_text, "text")
            canvas.itemconfigure(legenda_text, text=current + texto[index])
            root.after(25, lambda: delay_print(texto, index+1, callback))
        else:
            if callback:
                root.after(100, callback)

    # --- BOTÕES DE ESCOLHA ---
    choice_buttons = []
    def mostrar_opcoes(opcoes, callback):
        """Mostra botões de escolha na parte inferior da tela, ajustando largura automaticamente."""
        for btn in choice_buttons:
            btn.destroy()
        choice_buttons.clear()

        win_w = root.winfo_width()
        win_h = root.winfo_height()
        num_opcoes = len(opcoes)
        spacing = 20
        max_btn_width = (win_w - spacing*(num_opcoes+1)) // num_opcoes

        for i, (txt, val) in enumerate(opcoes):
            btn = tk.Button(root, text=txt, font=("Comic Sans MS", 16, "bold"),
                            bg="#222", fg="white", wraplength=max_btn_width-20,
                            justify="center", command=lambda v=val: callback(v))
            x_pos = spacing + i*(max_btn_width + spacing)
            btn.place(x=x_pos, y=win_h-90, width=max_btn_width, height=70)
            choice_buttons.append(btn)

    # --- FUNÇÃO PARA MOSTRAR PERSONAGEM NA TELA ---
    def mostrar_personagem(nome, x_perc, win_w, win_h, npc=False):
        """Mostra personagem dimensionada e posicionada acima da legenda."""
        img = personagens_imgs.get(nome)
        if not img:
            return
        MAX_H = int(win_h * 0.6)
        # Correção: remover multiplicação por 10 que escalava exageradamente as sprites
        scale = min(MAX_H / img.height, 1) * 10
        new_w, new_h = int(img.width * scale), int(img.height * scale)
        # Evitar tamanho 0
        new_w = max(1, new_w)
        new_h = max(1, new_h)
        img_resized = img.resize((new_w, new_h), Image.NEAREST)
        tk_img = ImageTk.PhotoImage(img_resized)

        legenda_h = 400
        y_pos = win_h - legenda_h - new_h + 30
        x_pos = int(win_w * x_perc)

        canvas.create_image(x_pos, y_pos, image=tk_img, anchor="center", tags="personagem")
        if npc:
            npc_img_ref.clear()
            npc_img_ref.append(tk_img)  # guarda referência para o NPC
        else:
            main_img_ref.append(tk_img)  # guarda referência para o personagem principal

    # --- FUNÇÃO DE DESENHO DA CENA ---
    def draw_scene(event=None):
        """Desenha background, caixa de legenda, personagens e HUD."""
        win_w, win_h = root.winfo_width(), root.winfo_height()

        # NÃO APAGA TUDO — mantém o texto da legenda
        canvas.delete("personagem")
        canvas.delete("fundo")
        canvas.delete("legenda_caixa")

        # --- Background ---
        scale_bg = min(win_w/fundo_original.width, win_h/fundo_original.height)
        new_w, new_h = int(fundo_original.width*scale_bg), int(fundo_original.height*scale_bg)
        bg_scaled = fundo_original.resize((new_w, new_h), Image.NEAREST)
        bg_tk = ImageTk.PhotoImage(bg_scaled)
        canvas.bg_ref = bg_tk
        canvas.create_image(win_w//2, win_h//2, image=bg_tk, anchor="center", tags="fundo")
        canvas.tag_raise(legenda_text)

        # --- Caixa de legenda ---
        legenda_h = 800
        legenda_w = max(300, win_w - 850)
        # proteger contra tamanhos inválidos
        try:
            legenda_resized = legenda_original.resize((legenda_w, legenda_h), Image.NEAREST)
        except Exception:
            legenda_resized = Image.new("RGBA", (legenda_w, legenda_h), (50,50,50,200))
        legenda_tk = ImageTk.PhotoImage(legenda_resized)
        canvas.legenda_ref = legenda_tk
        legenda_x, legenda_y = 425, win_h - legenda_h +60
        canvas.create_image(legenda_x, legenda_y, image=legenda_tk, anchor="nw",  tags="legenda_caixa")
        canvas.tag_raise(legenda_text)

        # --- HUD ---
        canvas.coords(hud_text, win_w-5, 30)
        atualizar_hud()

        # --- Personagens ---
        mostrar_personagem("principal", 0.3, win_w, win_h, npc=False)
        if npc_atual:  # mostrar NPC atual
            mostrar_personagem(npc_atual, 0.7, win_w, win_h, npc=True)

        canvas.coords(legenda_text, legenda_x + 320, legenda_y +300)
        # correção: usar a variável legenda_text (id) em vez de canvas.legenda_text que não existe
        canvas.itemconfigure(legenda_text, width=legenda_w - 80)
        canvas.tag_raise(legenda_text)

    # --- NOVA FUNÇÃO PARA ATUALIZAR NPC ---
    def atualizar_npc(nome):
        nonlocal npc_atual
        npc_atual = nome
        draw_scene()

    # --- HISTÓRIA DO JOGO ---
    def historia():
        """Sequência de eventos do jogo com delay e escolhas."""

        def etapa_boas_vindas():
            atualizar_legenda("")
            delay_print(f"🛡️ Bem-vindo, {personagem['name']}! Iniciando aventura em Nervalia...", callback=etapa_rei)

        def etapa_rei():
            atualizar_npc("rei")  # NPC Rei aparece
            mostrar_opcoes([("✅ Sim", True), ("❌ Não", False)], resposta_rei)
            atualizar_legenda("🤴 O Rei Cogumelo pergunta se queres aceitar a missão de resgatar a princesa Seya.")

        def resposta_rei(res):
            if not res:
                atualizar_legenda("💔 Desististe da missão. A princesa Seya ficou presa para sempre.")
                delay_print("", callback=finalizar)
            else:
                atualizar_legenda("⚔️ Coragem! O Rei confia em ti para esta missão.")
                delay_print("", callback=etapa_animal)

        def etapa_animal():
            atualizar_npc("rei")  # O Rei continua visível
            mostrar_opcoes([("🐖 Porco", "porco"), ("🦅 Águia", "aguia"), ("🐕 Cão", "cao"), ("🚶 Nenhum", None)], resposta_animal)
            atualizar_legenda("🗺️ O Rei oferece um mapa e pergunta se queres um animal para te acompanhar.")

        def resposta_animal(res):
            if res == "porco":
                personagem['coins'] += 10
                personagem['inventory'].append("🐖 Porco")
            elif res == "aguia":
                personagem['xp'] += 5
                personagem['inventory'].append("🦅 Águia")
            elif res == "cao":
                personagem['hp'] += 10
                personagem['inventory'].append("🐕 Cão")
                personagem['coins'] += 10
            atualizar_hud()
            delay_print(f"💰 Recebeste 10 moedas de ouro!", callback=etapa_bandidos)

        def etapa_bandidos():
            atualizar_npc("vilao")  # Mostra os bandidos (Cogumelo Mau)
            mostrar_opcoes([("⚔️ Atacar (-5 HP)", "atacar"), ("💰 Dar moedas (-5 moedas)", "dar")], resposta_bandidos)
            atualizar_legenda("🏞️ Ao sair do castelo, encontras bandidos pedindo 5 moedas.")

        def resposta_bandidos(res):
            if res == "atacar":
                personagem['hp'] -= 5
                atualizar_hud()
                delay_print("🩸 Sofreste alguns golpes, mas derrotaste os bandidos.", callback=etapa_loja)
            else:
                personagem['coins'] = max(0, personagem['coins'] - 5)
                atualizar_hud()
                delay_print("💵 Entregaste as moedas e seguiste viagem.", callback=etapa_loja)

        def etapa_loja():
            atualizar_npc("HomemMercado")  # Nenhum NPC na loja
            mostrar_opcoes([("🥤 Aceitar", True), ("❌ Recusar", False)], resposta_loja)
            atualizar_legenda("🏪 Encontras uma loja estranha. O vendedor oferece uma poção (+5 HP por 5 moedas).")

        def resposta_loja(res):
            if res:
                if personagem['coins'] >= 5:
                    personagem['coins'] -= 5
                    personagem['hp'] += 5
                    personagem['inventory'].append("🧪 Poção")
                    atualizar_hud()
                    delay_print("💖 Bebeste a poção e recuperaste 5 de HP.", callback=etapa_mulher)
                else:
                    delay_print("🚫 Não tens moedas suficientes!", callback=etapa_mulher)
            else:
                delay_print("🚶 Decidiste não arriscar e seguiste viagem.", callback=etapa_mulher)

        def etapa_mulher():
            atualizar_npc("mulher")  # Mulher aparece
            mostrar_opcoes([("💰 Ajudar", True), ("❌ Recusar", False)], resposta_mulher)
            atualizar_legenda("👩 Uma mulher pobre com 3 filhos pede 3 moedas.")

        def resposta_mulher(res):
            if res:
                if personagem['coins'] >= 3:
                    personagem['coins'] -= 3
                    atualizar_hud()
                    delay_print("🙏 A mulher agradece emocionada.", callback=etapa_floresta)
                else:
                    personagem['hp'] -= 2
                    atualizar_hud()
                    delay_print("😢 Não tinhas moedas. Perdes 2 HP pela culpa.", callback=etapa_floresta)
            else:
                personagem['hp'] -= 5
                atualizar_hud()
                delay_print("😢 Ignoraste a mulher e perdes 5 HP.", callback=etapa_floresta)

        def etapa_floresta():
            atualizar_npc("vilao")  # Cogumelos maus na floresta
            mostrar_opcoes([("🌲 Seguir pelo caminho seguro", "seguro"), ("🌳 Atravessar a floresta escura", "floresta")], resposta_floresta)
            atualizar_legenda("🌲 Chegaste a uma floresta. Um caminho seguro ou atravessar a floresta escura?")

        def resposta_floresta(res):
            if res == "seguro":
                personagem['xp'] += 10
                delay_print("🏞️ Seguiste pelo caminho seguro e economizaste HP.", callback=etapa_dragao)
            else:
                personagem['hp'] -= 10
                delay_print("👹 A floresta escura estava cheia de monstros. Perdes 10 HP.", callback=etapa_dragao)
                atualizar_hud()

        def etapa_dragao():
            atualizar_npc("Dragao")  # Dragão ou vilão final, mantém NPC visível
            mostrar_opcoes([("⚔️ Lutar com o dragão", "lutar"), ("🏃 Fugir", "fugir")], resposta_dragao)
            atualizar_legenda("🐉 Um dragão feroz bloqueia o teu caminho até ao castelo da princesa Seya.")

        def resposta_dragao(res):
            if res == "lutar":
                if "🧪 Poção" in personagem['inventory']:
                    personagem['hp'] -= 5
                    delay_print("💥 Usaste a poção para ganhar vantagem. Sofreste apenas 5 HP e derrotaste o dragão!", callback=etapa_castelo)
                else:
                    personagem['hp'] -= 20
                    if personagem['hp'] <= 0:
                        atualizar_legenda("💀 Sofreste demasiado dano. Morreste nas mãos do dragão!")
                        delay_print("", callback=finalizar)
                        return
                    delay_print("💥 Lutaste bravamente mas sofreste 20 HP. Conseguistes derrotar o dragão!", callback=etapa_castelo)
            else:
                personagem['coins'] = max(0, personagem['coins'] - 10)
                delay_print("🏃 Fugiste mas perdeste 10 moedas. O dragão continua a vigiar o castelo!", callback=etapa_castelo)
                atualizar_hud()

        def etapa_castelo():
            atualizar_npc(None)  # Nenhum NPC no castelo
            mostrar_opcoes([("🗝️ Usar chave mágica", True), ("💣 Forçar a porta", False)], resposta_castelo)
            atualizar_legenda("🏰 Chegaste ao castelo da princesa Seya. A porta está trancada.")

        def resposta_castelo(res):
            if res:
                personagem['inventory'].append("🗝️ Chave Mágica")
                delay_print("🔑 Usaste a chave mágica e abriste a porta sem problemas!", callback=etapa_princesa)
            else:
                personagem['hp'] -= 10
                delay_print("💥 Tentaste forçar a porta e sofrestes 10 HP!", callback=etapa_princesa)
                atualizar_hud()

        def etapa_princesa():
            atualizar_npc("princesa")  # A princesa pode ser representada pelo principal ou outro NPC
            mostrar_opcoes([("👸 Salvar a princesa Seya", True), ("🚪 Ignorar e fugir", False)], resposta_princesa)
            atualizar_legenda("👑 Finalmente encontraste a princesa Seya!")

        def resposta_princesa(res):
            if res:
                delay_print("🎉 Conseguiste salvar a princesa Seya! Nervalia está em paz. Recebes 50 moedas de recompensa e um tesouro misterioso.", callback=finalizar)
                personagem['coins'] += 50
                personagem['inventory'].append("🎁 Tesouro Misterioso")
            else:
                personagem['hp'] -= 15
                delay_print("💀 Ignoraste a princesa Seya. Ela permanece presa e perdes 15 HP pelo peso da culpa.", callback=finalizar)
                atualizar_hud()

        def finalizar():
            personagens = carregar_personagens()
            for p in personagens:
                if p['id'] == personagem['id']:
                    p.update(personagem)
                    break
            salvar_personagens(personagens)
            delay_print("🏁 Fim desta aventura! Boa sorte na próxima jornada.", callback=root.destroy)

        etapa_boas_vindas()

    # --- BIND PARA REDIMENSIONAMENTO E LOOP ---
    root.bind("<Configure>", draw_scene)
    root.after(100, draw_scene)

    # A história só começa depois que a janela está criada
    root.after(100, historia)

    root.mainloop()