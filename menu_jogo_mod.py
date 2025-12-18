import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import sys

# --- IMPORTAÇÕES DAS FUNÇÕES REAIS ---
from listar_personagens_mod import listar_personagens
from Criar_personagem_mod import criar_personagem
from editar_personagem_mod import editar_personagem
from Apagar_personagem_mod import apagar_personagem
from Jogar_cena_mod import jogar_cena
from Ver_estatisticas_mod import ver_estatisticas
from Exportar_personagens_mod import exportar_personagens
from importar_personagens_mod import importar_personagens

# --- CONFIGURAÇÕES VISUAIS ---
BG_COLOR = "#0D0D0D"
BUTTON_PLACEHOLDER_COLOR = "#FF6347"
BG_PLACEHOLDER_COLOR = "#1a1a1a"

# --- DIMENSÕES ESPERADAS DA ARTE ORIGINAL ---
BG_ORIGINAL_W = 1200
BG_ORIGINAL_H = 675
BUTTON_ORIGINAL_W = 180
BUTTON_ORIGINAL_H = 45

# --- NOME DO ARQUIVO DE FUNDO ---
BG_FILENAME = "fundomenu1.png"

# --- BASE DIR ---
def get_base_dir():
    try:
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()

BASE_DIR = get_base_dir()

# --- FUNÇÃO PARA CARREGAR IMAGEM ---
def load_image(filename, is_background=False):
    filepath = os.path.join(BASE_DIR, filename)
    try:
        img = Image.open(filepath).convert("RGBA")
        print(f"Sucesso ao carregar: {filename}")
        return img
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filename}' não encontrado em: {BASE_DIR}")
        color = BG_PLACEHOLDER_COLOR if is_background else BUTTON_PLACEHOLDER_COLOR
        size = (BG_ORIGINAL_W, BG_ORIGINAL_H) if is_background else (BUTTON_ORIGINAL_W, BUTTON_ORIGINAL_H)
        placeholder = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(placeholder)
        font = ImageFont.load_default()
        text = f"{filename} (FALHOU)"
        bbox = draw.textbbox((0, 0), text, font=font)
        textwidth = bbox[2] - bbox[0]
        textheight = bbox[3] - bbox[1]
        draw.text(((size[0] - textwidth) // 2, (size[1] - textheight) // 2),
                  text, font=font, fill="white")
        return placeholder

# ===============================================================
#                  ÁREA DO JOGADOR (INTERFACE)
# ===============================================================
def menu_jogo_mod(user):
    """Interface gráfica do menu principal do jogador."""
    root = tk.Tk()
    root.title(f"Nervalia - Área do Jogador: {user}")
    root.configure(bg=BG_COLOR)
    root.state("zoomed")
    root.resizable(True, True)
    canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- CARREGAR IMAGENS ---
    bg_original = load_image(BG_FILENAME, is_background=True)
    TITLE_FILENAME = "Areadojogador.png"
    title_image = load_image(TITLE_FILENAME)
    bg_w, bg_h = bg_original.size

    # --- FUNÇÕES DE BOTÃO INTEGRADAS (fecham janela antes de executar) ---
    def action_and_close(func):
        def wrapper():
            root.destroy()
            func(user)
        return wrapper

    def reopen_menu():
     root.destroy()
     # import local pra evitar circular import
     from menu_mod import menu_mod
     menu_mod()

    FUNC_MAP = {
        "jogar_cena": action_and_close(jogar_cena),
        "listar": action_and_close(listar_personagens),
        "criar": action_and_close(criar_personagem),
        "editar": action_and_close(editar_personagem),
        "apagar": action_and_close(apagar_personagem),
        "estatisticas": action_and_close(ver_estatisticas),
        "exportar": action_and_close(exportar_personagens),
        "importar": action_and_close(importar_personagens),
        "voltar": reopen_menu,  # reabre o menu
    }

    BUTTON_ORDER = list(FUNC_MAP.keys())

    # --- NOMES ATUALIZADOS DAS ARTES ---
    CUSTOM_FILENAME_MAP = {
        "jogar_cena": "jogarbotao.png",
        "listar": "Listar.png",
        "criar": "criar.png",
        "editar": "Editar.png",
        "apagar": "Apagar.png",
        "estatisticas": "Ver.png",
        "exportar": "Exportar.png",
        "importar": "Importar.png",
        "voltar": "Voltar.png",
    }

    BUTTON_IMAGES = {}
    for name in BUTTON_ORDER:
        filename = CUSTOM_FILENAME_MAP.get(name, f"{name}_btn.png")
        BUTTON_IMAGES[name] = load_image(filename)

    # --- POSIÇÕES E CONFIGURAÇÕES DOS BOTÕES ---
    BUTTON_VISUAL_REDUCTION_FACTOR = 0.7
    BUTTON_Y_START = 35
    BUTTON_HEIGHT = 7
    BUTTON_SPACING = 4
    BUTTON_INDIVIDUAL_SCALE = {"listar": 0.95}

    # --- FUNÇÃO DE DESENHO ---
    def draw_scene(event=None):
        nonlocal bg_w, bg_h
        canvas.delete("all")
        win_w, win_h = root.winfo_width(), root.winfo_height()
        if win_w < 50 or win_h < 50:
            return
        if bg_w == 0 or bg_h == 0:
            bg_w, bg_h = BG_ORIGINAL_W, BG_ORIGINAL_H

        scale = min(win_w / bg_w, win_h / bg_h)
        new_w, new_h = int(bg_w * scale), int(bg_h * scale)
        try:
            bg_scaled = bg_original.resize((new_w, new_h), Image.NEAREST)
            bg_tk = ImageTk.PhotoImage(bg_scaled)
            canvas.bg_ref = bg_tk
            canvas.create_image(win_w // 2, win_h // 2, image=bg_tk, anchor="center")
        except Exception as e:
            print(f"Erro ao desenhar fundo: {e}")
            return

        offset_x = (win_w - new_w) // 2
        offset_y = (win_h - new_h) // 2
        image_refs = []
        button_areas = []

        for i, name in enumerate(BUTTON_ORDER):
            img = BUTTON_IMAGES[name]
            w, h = img.size
            individual_factor = BUTTON_INDIVIDUAL_SCALE.get(name, 1.0)
            button_scale = scale * BUTTON_VISUAL_REDUCTION_FACTOR * individual_factor
            sw, sh_img = int(w * button_scale), int(h * button_scale)
            img_tk = ImageTk.PhotoImage(img.resize((sw, sh_img), Image.NEAREST))
            image_refs.append(img_tk)

            y_pos_original = BUTTON_Y_START + i * (BUTTON_HEIGHT + BUTTON_SPACING)
            final_y_hitbox = int(y_pos_original * scale) + offset_y
            padding_y_original = (h - BUTTON_HEIGHT) / 2
            padding_offset_y_scaled = int(padding_y_original * button_scale)
            center_x_relative = new_w // 2
            button_start_x_relative = center_x_relative - (sw // 2)
            final_x = button_start_x_relative + offset_x
            final_y_image = final_y_hitbox - padding_offset_y_scaled

            if name == "listar":
                final_y_image += int(2 * scale)

            canvas.create_image(final_x, final_y_image, image=img_tk, anchor="nw")
            h_scaled = int(BUTTON_HEIGHT * button_scale)
            x1, y1 = final_x, final_y_hitbox
            x2, y2 = final_x + sw, final_y_hitbox + h_scaled
            button_areas.append((x1, y1, x2, y2, FUNC_MAP[name]))

        canvas.image_refs = image_refs
        canvas.button_areas = button_areas

        # --- Título ---
        try:
            title_scale = scale * 0.3
            tw, th = title_image.size
            integer_scale = max(1, int(title_scale * 2))
            new_tw, new_th = tw * integer_scale, th * integer_scale
            title_tk = ImageTk.PhotoImage(title_image.resize((new_tw, new_th), Image.NEAREST))
            canvas.image_refs.append(title_tk)
            title_x = win_w // 2
            title_y = offset_y + int(-7 * scale)
            canvas.create_image(title_x, title_y, image=title_tk, anchor="n")
        except Exception as e:
            print(f"Erro ao desenhar título: {e}")

    # --- CLIQUES ---
    def on_click(event):
        if not hasattr(canvas, 'button_areas'):
            return
        for x1, y1, x2, y2, func in canvas.button_areas:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                func()
                break

    # --- INICIALIZAÇÃO ---
    canvas.bind("<Button-1>", on_click)
    root.bind("<Configure>", draw_scene)
    root.after(100, draw_scene)
    root.mainloop()

# ===============================================================
# TESTE DIRETO (opcional)
# ===============================================================
if __name__ == "__main__":
    menu_jogo_mod("JogadorTeste")
