# main.py
from src.simulacao_nucleo import iniciar_simulacao_completa

def escolher_cenario_simulacao():
    #Pede ao usuário para escolher o cenário.
    while True:
        print("\nEscolha o Cenário para Simular:")
        print("1: Cenário 1 (1 Carro, 65 Passageiros, Capacidade 5)")
        print("2: Cenário 2 (2 Carros, 65 Passageiros, Capacidade 5)")
        print("3: Cenário N (N Carros, 1000 Passageiros, Capacidade 10)")
        
        try:
            escolha = int(input("Digite o número do cenário (1, 2 ou 3): "))
            if escolha in [1, 2, 3]:
                return escolha
            else:
                print("Opção inválida. Por favor, escolha 1, 2 ou 3.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

if __name__ == "__main__":
    numero_cenario_escolhido = escolher_cenario_simulacao()
    iniciar_simulacao_completa(numero_cenario_escolhido)