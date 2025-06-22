# src/simulacao_nucleo.py (VERSÃO FINAL CORRIGIDA)
import threading
import time
import random
import logging
import pygame
import sys    

from .constantes import obter_parametros_cenario, calcular_tempo_individual_passageiro_embarque
from .estado_compartilhado import EstadoCompartilhado
from .passageiro_logica import executar_logica_passageiro
from .carro_logica import executar_logica_carro

# --- Constantes da GUI (NO LUGAR CERTO AGORA) ---
LARGURA_TELA = 1000
ALTURA_TELA = 700  
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
ROXO = (128, 0, 128)
LARANJA = (255, 165, 0)
CIANO = (0, 255, 255)
CORES_CARROS = [VERMELHO, VERDE, AZUL, ROXO, LARANJA, CIANO] 

def desenhar_cenario_visual(tela_pygame, obj_estado, params_cenario):
    # Esta função está correta, não precisa de alterações.
    # Vou colar seu código original aqui.
    tela_pygame.fill(PRETO) 

    fonte_padrao = pygame.font.Font(None, 30)
    fonte_pequena = pygame.font.Font(None, 24)
    fonte_status_carro = pygame.font.Font(None, 20)
    fonte_id_carro = pygame.font.Font(None, 28)
    fonte_passageiro_transito = pygame.font.Font(None, 22)

    rect_estacao = pygame.Rect(50, 550, 200, 100) 
    pygame.draw.rect(tela_pygame, BRANCO, rect_estacao, 2) 
    surf_label_estacao = fonte_padrao.render('Estação', True, BRANCO)
    tela_pygame.blit(surf_label_estacao, (rect_estacao.centerx - surf_label_estacao.get_width() // 2, rect_estacao.centery - surf_label_estacao.get_height() // 2))

    rect_area_fila = pygame.Rect(300, 550, 650, 100) 
    pygame.draw.rect(tela_pygame, AMARELO, rect_area_fila, 1)
    surf_titulo_fila = fonte_padrao.render('Fila de Espera', True, AMARELO)
    tela_pygame.blit(surf_titulo_fila, (rect_area_fila.left + 10, rect_area_fila.top - 30))

    trilho_centro_x, trilho_centro_y, trilho_raio = 500, 250, 150
    pygame.draw.circle(tela_pygame, AZUL, (trilho_centro_x, trilho_centro_y), trilho_raio, 3) 
    surf_label_passeio = fonte_padrao.render('Passeio', True, AZUL)
    tela_pygame.blit(surf_label_passeio, (trilho_centro_x - surf_label_passeio.get_width() // 2, trilho_centro_y - trilho_raio - surf_label_passeio.get_height() - 10))

    obj_estado.trava_acesso_geral.acquire()
    num_passageiros_fila_atual = obj_estado.passageiros_na_fila_contador
    copia_ids_na_fila = list(obj_estado.fila_de_espera_passageiros) 
    copia_status_carros = dict(obj_estado.status_visual_carros)
    copia_passageiros_carros = {k: list(v) for k, v in obj_estado.passageiros_dentro_dos_carros_mapa.items()}
    copia_transito_embarque = dict(obj_estado.mapa_passageiro_transitando_para_embarque)
    copia_transito_desembarque = dict(obj_estado.mapa_passageiro_transitando_para_desembarque)
    total_passageiros_sim = params_cenario["NUM_PASSAGEIROS"]
    passageiros_ja_transportados_gui = obj_estado.passageiros_transportados_contador
    id_carro_ativo_embarque_gui = obj_estado.id_carro_processando_embarque
    obj_estado.trava_acesso_geral.release()

    surf_num_fila = fonte_pequena.render(f"Fila: {num_passageiros_fila_atual}", True, AMARELO)
    tela_pygame.blit(surf_num_fila, (rect_area_fila.left + 10, rect_area_fila.top + 10))

    raio_dot_passageiro_fila = 4
    espaco_dot_x_fila = 10
    espaco_dot_y_fila = 10
    dots_por_linha_fila = rect_area_fila.width // espaco_dot_x_fila
    x_inicial_fila = rect_area_fila.left + raio_dot_passageiro_fila + 2
    y_inicial_fila = rect_area_fila.top + 40 
    for i, _ in enumerate(copia_ids_na_fila):
        linha = i // dots_por_linha_fila
        coluna = i % dots_por_linha_fila
        dot_x_calc = x_inicial_fila + coluna * espaco_dot_x_fila
        dot_y_calc = y_inicial_fila + linha * espaco_dot_y_fila
        if dot_y_calc + raio_dot_passageiro_fila < rect_area_fila.bottom - 5:
            pygame.draw.circle(tela_pygame, AMARELO, (dot_x_calc, dot_y_calc), raio_dot_passageiro_fila)
        else:
            surf_texto_extra_fila = fonte_pequena.render(f"+{num_passageiros_fila_atual - i}", True, AMARELO)
            tela_pygame.blit(surf_texto_extra_fila, (dot_x_calc, dot_y_calc - raio_dot_passageiro_fila*2)) 
            break
    
    largura_carro_desenho = 60
    altura_carro_desenho = 40
    y_pos_carros_garagem = rect_estacao.top - altura_carro_desenho - 40 
    espacamento_total_entre_carros = 100 

    for id_carro_loop_desenho in range(1, params_cenario["NUM_CARROS"] + 1):
        cor_do_carro_atual = CORES_CARROS[(id_carro_loop_desenho - 1) % len(CORES_CARROS)]
        status_do_carro_atual = copia_status_carros.get(id_carro_loop_desenho, "desconhecido")
        lista_passageiros_neste_carro = copia_passageiros_carros.get(id_carro_loop_desenho, [])
        
        x_pos_carro_garagem = 50 + (id_carro_loop_desenho - 1) * espacamento_total_entre_carros
        rect_final_carro_garagem = pygame.Rect(x_pos_carro_garagem, y_pos_carros_garagem, largura_carro_desenho, altura_carro_desenho)
        x_pos_carro_embarque = rect_estacao.centerx - largura_carro_desenho // 2
        y_pos_carro_embarque = rect_estacao.top - altura_carro_desenho - 5 
        rect_final_carro_embarque = pygame.Rect(x_pos_carro_embarque, y_pos_carro_embarque, largura_carro_desenho, altura_carro_desenho)
        x_pos_carro_passeio = trilho_centro_x - largura_carro_desenho // 2
        y_pos_carro_passeio = trilho_centro_y - altura_carro_desenho // 2
        rect_final_carro_passeio = pygame.Rect(x_pos_carro_passeio, y_pos_carro_passeio, largura_carro_desenho, altura_carro_desenho)
        
        rect_posicao_desenho_carro = rect_final_carro_garagem 

        if status_do_carro_atual == "embarcando" or (status_do_carro_atual == "estacao_pronto" and id_carro_ativo_embarque_gui == id_carro_loop_desenho):
            rect_posicao_desenho_carro = rect_final_carro_embarque
        elif status_do_carro_atual == "passeio":
            rect_posicao_desenho_carro = rect_final_carro_passeio
        elif status_do_carro_atual == "desembarcando":
            rect_posicao_desenho_carro = rect_final_carro_embarque
        
        pygame.draw.rect(tela_pygame, cor_do_carro_atual, rect_posicao_desenho_carro)
        surf_id_carro = fonte_id_carro.render(f"C{id_carro_loop_desenho}", True, PRETO)
        tela_pygame.blit(surf_id_carro, (rect_posicao_desenho_carro.centerx - surf_id_carro.get_width() // 2, rect_posicao_desenho_carro.centery - surf_id_carro.get_height() // 2))
        
        raio_dot_passageiro_carro = 3
        for i, _ in enumerate(lista_passageiros_neste_carro):
            if i < params_cenario["CAPACIDADE_CARRO"]:
                offset_x_interno_carro = (i % 5) * (largura_carro_desenho // 5) + raio_dot_passageiro_carro + 3
                offset_y_interno_carro = (i // 5) * (altura_carro_desenho // 2) + raio_dot_passageiro_carro + 3
                pygame.draw.circle(tela_pygame, BRANCO, (rect_posicao_desenho_carro.left + offset_x_interno_carro, rect_posicao_desenho_carro.top + offset_y_interno_carro), raio_dot_passageiro_carro)

        surf_status_carro = fonte_status_carro.render(status_do_carro_atual, True, BRANCO)
        tela_pygame.blit(surf_status_carro, (rect_posicao_desenho_carro.centerx - surf_status_carro.get_width() // 2, rect_posicao_desenho_carro.top - surf_status_carro.get_height() - 2))

    margem_transito_estacao = 10
    raio_dot_indicador_transito = 5

    id_pass_trans_embarque = copia_transito_embarque.get(id_carro_ativo_embarque_gui)
    if id_pass_trans_embarque is not None:
        surf_texto_trans_embarque = fonte_passageiro_transito.render(f"P{id_pass_trans_embarque} -> C{id_carro_ativo_embarque_gui}", True, AMARELO)
        x_pos_trans_embarque = rect_estacao.right - surf_texto_trans_embarque.get_width() - margem_transito_estacao
        y_pos_trans_embarque = rect_estacao.top + margem_transito_estacao
        pygame.draw.circle(tela_pygame, AMARELO, (x_pos_trans_embarque - raio_dot_indicador_transito - 2, y_pos_trans_embarque + surf_texto_trans_embarque.get_height()//2), raio_dot_indicador_transito)
        tela_pygame.blit(surf_texto_trans_embarque, (x_pos_trans_embarque, y_pos_trans_embarque))

    id_pass_trans_desembarque = copia_transito_desembarque.get(id_carro_ativo_embarque_gui)
    if id_pass_trans_desembarque is not None:
        surf_texto_trans_desembarque = fonte_passageiro_transito.render(f"P{id_pass_trans_desembarque} <- C{id_carro_ativo_embarque_gui}", True, BRANCO)
        x_pos_trans_desembarque = rect_estacao.left + margem_transito_estacao
        y_pos_trans_desembarque = rect_estacao.top + margem_transito_estacao
        pygame.draw.circle(tela_pygame, BRANCO, (x_pos_trans_desembarque + surf_texto_trans_desembarque.get_width() + raio_dot_indicador_transito + 2, y_pos_trans_desembarque + surf_texto_trans_desembarque.get_height()//2), raio_dot_indicador_transito)
        tela_pygame.blit(surf_texto_trans_desembarque, (x_pos_trans_desembarque, y_pos_trans_desembarque))

    surf_info_geral_1 = fonte_pequena.render(f"Transportados: {passageiros_ja_transportados_gui}/{total_passageiros_sim}", True, BRANCO)
    tela_pygame.blit(surf_info_geral_1, (10, 10))

    pygame.display.flip()

def iniciar_simulacao_completa(numero_cenario):
    params_cenario_atual = obter_parametros_cenario(numero_cenario)
    params_cenario_atual["TEMPO_INDIVIDUAL_EMBARQUE_DESEMBARQUE_SEG"] = calcular_tempo_individual_passageiro_embarque(params_cenario_atual)

    num_passageiros = params_cenario_atual["NUM_PASSAGEIROS"]
    num_carros = params_cenario_atual["NUM_CARROS"]
    
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s', datefmt='%H:%M:%S')

    tempo_de_inicio_simulacao = time.time() 
    logging.info(f"Simulação Iniciada: Cenário={params_cenario_atual['ID_CENARIO']}, P={num_passageiros}, C={num_carros}, Cap={params_cenario_atual['CAPACIDADE_CARRO']}")

    objeto_de_estado_compartilhado = EstadoCompartilhado(num_carros) 

    lista_de_threads_carros = []
    lista_de_threads_passageiros = []

    def gerenciador_de_criacao_de_passageiros(obj_estado, params):
        for i in range(params["NUM_PASSAGEIROS"]):
            obj_estado.trava_acesso_geral.acquire()
            if not obj_estado.simulacao_deve_continuar_ativa:
                obj_estado.trava_acesso_geral.release()
                break
            obj_estado.trava_acesso_geral.release()

            thread = threading.Thread(target=executar_logica_passageiro, args=(i + 1, obj_estado, params), name=f"Passageiro-{i+1}")
            thread.start() # Threads normais, não demônios
            lista_de_threads_passageiros.append(thread)
            
            intervalo = random.uniform(params["INTERVALO_MIN_CHEGADA_SEG"], params["INTERVALO_MAX_CHEGADA_SEG"]) 
            time.sleep(intervalo)
        logging.info("Gerenciador concluiu a criação de todos os passageiros.")

    for i in range(num_carros):
        thread = threading.Thread(target=executar_logica_carro, args=(i, objeto_de_estado_compartilhado, params_cenario_atual), name=f"Carro-{i+1}")
        thread.start() # Threads normais, não demônios
        lista_de_threads_carros.append(thread)

    thread_gerenciador = threading.Thread(target=gerenciador_de_criacao_de_passageiros, args=(objeto_de_estado_compartilhado, params_cenario_atual), name="GerenciadorPassageiros")
    thread_gerenciador.start()

    # --- Loop da GUI (agora dentro da função principal) ---
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(f"Simulação Montanha-Russa (Cenário {params_cenario_atual['ID_CENARIO']})")
    relogio_pygame = pygame.time.Clock()

    loop_gui_ativo = True
    while loop_gui_ativo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                loop_gui_ativo = False
                objeto_de_estado_compartilhado.trava_acesso_geral.acquire()
                objeto_de_estado_compartilhado.simulacao_deve_continuar_ativa = False 
                objeto_de_estado_compartilhado.trava_acesso_geral.release()

        # Condição para fechar a GUI automaticamente quando a simulação acabar
        objeto_de_estado_compartilhado.trava_acesso_geral.acquire()
        if objeto_de_estado_compartilhado.passageiros_transportados_contador >= num_passageiros:
            loop_gui_ativo = False
        objeto_de_estado_compartilhado.trava_acesso_geral.release()

        desenhar_cenario_visual(tela, objeto_de_estado_compartilhado, params_cenario_atual)
        relogio_pygame.tick(30)

    logging.info("Loop da GUI encerrado. Aguardando finalização das threads...")
    pygame.quit()

    # --- Lógica de Finalização (Join) ---
    thread_gerenciador.join()
    logging.info("Thread do gerenciador de passageiros finalizada.")

    for t_carro in lista_de_threads_carros:
        t_carro.join()
        logging.info(f"Thread {t_carro.name} finalizada.")

    for t_passageiro in lista_de_threads_passageiros:
        t_passageiro.join()
    logging.info("Todas as threads de passageiros finalizadas.")

    # --- Geração do Relatório ---
    tempo_de_fim_simulacao = time.time()
    logging.info("--- Relatório Final da Simulação ---")
    tempo_total_seg_sim = tempo_de_fim_simulacao - tempo_de_inicio_simulacao
    tempo_total_movimento_seg = objeto_de_estado_compartilhado.viagens_feitas_contador * params_cenario_atual["TEMPO_PASSEIO_SEG"]
    eficiencia_calculada = (tempo_total_movimento_seg / tempo_total_seg_sim) * 100 if tempo_total_seg_sim > 0 else 0

    if objeto_de_estado_compartilhado.lista_tempos_espera_fila:
        val_min_espera = min(objeto_de_estado_compartilhado.lista_tempos_espera_fila)
        val_max_espera = max(objeto_de_estado_compartilhado.lista_tempos_espera_fila)
        val_media_espera = sum(objeto_de_estado_compartilhado.lista_tempos_espera_fila) / len(objeto_de_estado_compartilhado.lista_tempos_espera_fila)
        logging.info(f"Tempo mínimo de espera na fila: {val_min_espera:.2f} seg")
        logging.info(f"Tempo máximo de espera na fila: {val_max_espera:.2f} seg")
        logging.info(f"Tempo médio de espera na fila:  {val_media_espera:.2f} seg")
    else:
        logging.info("Nenhum passageiro esperou na fila (ou dados não coletados).")

    logging.info(f"Tempo total de simulação: {tempo_total_seg_sim:.2f} seg ({tempo_total_seg_sim / 60.0:.2f} minutos)")
    logging.info(f"Número total de viagens realizadas: {objeto_de_estado_compartilhado.viagens_feitas_contador}")
    logging.info(f"Eficiência da Montanha Russa: {eficiencia_calculada:.2f}% (Tempo em movimento / Tempo total)")
    logging.info("Simulação Concluída.")