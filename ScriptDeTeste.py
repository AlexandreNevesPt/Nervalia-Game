from listar_personagens_mod import listar_personagens
from Criar_personagem_mod import criar_personagem
from editar_personagem_mod import editar_personagem
from Apagar_personagem_mod import apagar_personagem
from Jogar_cena_mod import jogar_cena
from Ver_estatisticas_mod import ver_estatisticas
from Exportar_personagens_mod import exportar_personagens
from importar_personagens_mod import importar_personagens


def menu_jogar(user):
    while True:
        print(f"\n=== Área do Jogador: {user} ===")
        print("1) Listar personagens")
        print("2) Criar personagem")
        print("3) Editar personagem (atributos simples)")
        print("4) Apagar personagem")
        print("5) Jogar cena com uma personagem")
        print("6) Ver estatísticas / relatórios")
        print("7) Exportar personagens")
        print("8) Importar personagens")
        print("0) Voltar ao Menu Principal")
        print("===============================")
        
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == "1":
            listar_personagens(user)
        elif escolha == "2":
            criar_personagem(user)
        elif escolha == "3":
            editar_personagem(user)
        elif escolha == "4":
            apagar_personagem(user)
        elif escolha == "5":
            jogar_cena(user)
        elif escolha == "6":
            ver_estatisticas(user)
        elif escolha == "7":
            exportar_personagens(user)
        elif escolha == "8":
            importar_personagens(user)
        elif escolha == "0":
            print("Voltando ao Menu Principal...")
            break
        else:
            print("Opção inválida! Tente novamente.")