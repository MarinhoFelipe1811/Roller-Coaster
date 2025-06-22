# src/estado_compartilhado.py
import threading
from collections import deque

class EstadoCompartilhado:
    def __init__(self, num_carros_param):
        self.passageiros_na_fila_contador = 0
        self.passageiros_transportados_contador = 0
        self.viagens_feitas_contador = 0
        self.fila_de_espera_passageiros = deque()
        self.lista_tempos_espera_fila = []
        self.id_carro_processando_embarque = -1
        self.simulacao_deve_continuar_ativa = True

        # Semáforos
        self.trava_acesso_geral = threading.Semaphore(1)
        self.semaforo_passageiro_na_fila = threading.Semaphore(0)
        self.semaforo_carro_pode_chamar_passageiro = threading.Semaphore(0)
        self.semaforo_passageiro_confirmou_embarque = threading.Semaphore(0)
        self.semaforo_carro_pode_liberar_passageiro = threading.Semaphore(0)
        self.semaforo_passageiro_confirmou_desembarque = threading.Semaphore(0)
        # Garante que o primeiro carro (índice 0) comece com o turno.
        self.semaforos_turno_dos_carros = [threading.Semaphore(1 if i == 0 else 0) for i in range(num_carros_param)]

        self.trilho_esta_livre = threading.Semaphore(1)
        
        # Estados para a GUI
        self.status_visual_carros = {i + 1: "estacao" for i in range(num_carros_param)}
        self.passageiros_dentro_dos_carros_mapa = {i + 1: [] for i in range(num_carros_param)}
        self.mapa_passageiro_transitando_para_embarque = {i + 1: None for i in range(num_carros_param)}
        self.mapa_passageiro_transitando_para_desembarque = {i + 1: None for i in range(num_carros_param)}