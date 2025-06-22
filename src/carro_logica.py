import time
import logging
import threading

def executar_logica_carro(id_carro_base_zero, obj_estado, params_cenario):
    num_total_de_carros = params_cenario["NUM_CARROS"]
    num_total_de_passageiros_sim = params_cenario["NUM_PASSAGEIROS"]
    capacidade_do_carro = params_cenario["CAPACIDADE_CARRO"]
    duracao_passeio_seg = params_cenario["TEMPO_PASSEIO_SEG"]

    id_proximo_carro_array = (id_carro_base_zero + 1) % num_total_de_carros
    id_carro_para_exibicao = id_carro_base_zero + 1

    logging.info(f"Carro {id_carro_para_exibicao} iniciado.")

    while True:
        # 1. Espera pelo seu turno para usar a estação de embarque.
        obj_estado.semaforos_turno_dos_carros[id_carro_base_zero].acquire()

        # 2. Verifica se a simulação deve terminar.
        obj_estado.trava_acesso_geral.acquire()
        todos_passageiros_ja_passaram = obj_estado.passageiros_transportados_contador >= num_total_de_passageiros_sim
        if todos_passageiros_ja_passaram:
            obj_estado.simulacao_deve_continuar_ativa = False # Sinaliza para os passageiros pararem de chegar
            obj_estado.status_visual_carros[id_carro_para_exibicao] = "encerrado"
            obj_estado.trava_acesso_geral.release()
            
            # Acorda o próximo carro para que ele também possa verificar e encerrar.
            obj_estado.semaforos_turno_dos_carros[id_proximo_carro_array].release()
            logging.info(f"Carro {id_carro_para_exibicao} encerrando: todos os {num_total_de_passageiros_sim} passageiros foram transportados.")
            break # Encerra a thread do carro.
        
        # Se chegou aqui, a simulação continua. Libera a trava por enquanto.
        obj_estado.trava_acesso_geral.release()

        # 3. Lógica para embarcar passageiros.
        # Primeiro, calcula quantos passageiros precisa, respeitando a capacidade e o total restante.
        obj_estado.trava_acesso_geral.acquire()
        passageiros_restantes_na_simulacao = num_total_de_passageiros_sim - obj_estado.passageiros_transportados_contador
        obj_estado.trava_acesso_geral.release()
        
        passageiros_necessarios = min(capacidade_do_carro, passageiros_restantes_na_simulacao)

        if passageiros_necessarios == 0: # Não deveria acontecer por causa do check anterior, mas é uma segurança.
             obj_estado.semaforos_turno_dos_carros[id_proximo_carro_array].release()
             continue

        # Espera que o número necessário de passageiros entre na fila.
        for _ in range(passageiros_necessarios):
            obj_estado.semaforo_passageiro_na_fila.acquire()
        
        # --- INÍCIO DO PROCESSO DE EMBARQUE REAL ---
        obj_estado.trava_acesso_geral.acquire()
        
        # CORREÇÃO: Usando o nome correto da variável, declarado em estado_compartilhado.py
        obj_estado.id_carro_processando_embarque = id_carro_para_exibicao
        obj_estado.status_visual_carros[id_carro_para_exibicao] = "embarcando"
        
        # Retira os passageiros da fila de espera e coloca na lista local para esta viagem
        ids_passageiros_para_esta_viagem = []
        for _ in range(passageiros_necessarios):
            if obj_estado.fila_de_espera_passageiros:
                id_p = obj_estado.fila_de_espera_passageiros.popleft()
                ids_passageiros_para_esta_viagem.append(id_p)
                obj_estado.passageiros_na_fila_contador -= 1
            else:
                logging.error(f"Carro {id_carro_para_exibicao} - ERRO CRÍTICO: Fila vazia, mas semáforos indicavam o contrário!")
                break
        
        obj_estado.trava_acesso_geral.release()

        if not ids_passageiros_para_esta_viagem:
            logging.warning(f"Carro {id_carro_para_exibicao}: Não embarcou ninguém. Liberando estação.")
            obj_estado.semaforos_turno_dos_carros[id_proximo_carro_array].release()
            continue
        
        logging.info(f"Carro {id_carro_para_exibicao} iniciou embarque para: {ids_passageiros_para_esta_viagem}.")

        # Sincroniza o embarque um por um
        for id_passageiro_embarcando in ids_passageiros_para_esta_viagem:
            obj_estado.semaforo_carro_pode_chamar_passageiro.release()
            obj_estado.semaforo_passageiro_confirmou_embarque.acquire()
            obj_estado.trava_acesso_geral.acquire()
            obj_estado.passageiros_dentro_dos_carros_mapa[id_carro_para_exibicao].append(id_passageiro_embarcando)
            obj_estado.trava_acesso_geral.release()
        
        logging.info(f"Carro {id_carro_para_exibicao} terminou o embarque com {len(ids_passageiros_para_esta_viagem)} passageiros.")

        # --- LÓGICA DE PASSEIO COM TRILHO ÚNICO ---
        logging.info(f"Carro {id_carro_para_exibicao} está pronto e aguardando o TRILHO...")
        obj_estado.trilho_esta_livre.acquire() # Espera o trilho ficar livre
        logging.info(f"Carro {id_carro_para_exibicao} pegou o trilho e vai partir.")

        # AGORA que pegou o trilho, libera a ESTAÇÃO para o próximo carro (se houver)
        if num_total_de_carros > 1:
             logging.info(f"Carro {id_carro_para_exibicao} partindo, liberando estação para Carro {id_proximo_carro_array + 1}.")
             obj_estado.semaforos_turno_dos_carros[id_proximo_carro_array].release()

        obj_estado.trava_acesso_geral.acquire()
        obj_estado.status_visual_carros[id_carro_para_exibicao] = "passeio"
        obj_estado.trava_acesso_geral.release()

        logging.info(f"Carro {id_carro_para_exibicao} começou o passeio (duração {duracao_passeio_seg}s).")
        time.sleep(duracao_passeio_seg)
        
        # --- PROCESSO DE DESEMBARQUE ---
        obj_estado.trava_acesso_geral.acquire()
        obj_estado.viagens_feitas_contador += 1
        obj_estado.status_visual_carros[id_carro_para_exibicao] = "desembarcando"
        # CORREÇÃO: Usando o nome correto da variável
        obj_estado.id_carro_processando_embarque = id_carro_para_exibicao # Reafirma qual carro está ativo
        ids_para_desembarcar = list(obj_estado.passageiros_dentro_dos_carros_mapa[id_carro_para_exibicao])
        obj_estado.trava_acesso_geral.release()

        logging.info(f"Carro {id_carro_para_exibicao} retornou e iniciou desembarque de: {ids_para_desembarcar}.")
        
        for id_passageiro_desembarcando in ids_para_desembarcar:
            obj_estado.semaforo_carro_pode_liberar_passageiro.release()
            obj_estado.semaforo_passageiro_confirmou_desembarque.acquire()
            obj_estado.trava_acesso_geral.acquire()
            obj_estado.passageiros_transportados_contador += 1
            if id_passageiro_desembarcando in obj_estado.passageiros_dentro_dos_carros_mapa[id_carro_para_exibicao]:
                 obj_estado.passageiros_dentro_dos_carros_mapa[id_carro_para_exibicao].remove(id_passageiro_desembarcando)
            obj_estado.trava_acesso_geral.release()
            
        logging.info(f"Carro {id_carro_para_exibicao} terminou desembarque.")
        obj_estado.trava_acesso_geral.acquire()
        obj_estado.id_carro_processando_embarque = -1 # Libera o "carro ativo"
        obj_estado.trava_acesso_geral.release()

        # Libera o trilho APÓS o desembarque estar completo.
        logging.info(f"Carro {id_carro_para_exibicao} liberou o trilho.")
        obj_estado.trilho_esta_livre.release()
        
        # Se for o único carro, ele precisa devolver o turno para si mesmo.
        if num_total_de_carros == 1:
            obj_estado.semaforos_turno_dos_carros[id_carro_base_zero].release()

    logging.info(f"Carro {id_carro_para_exibicao} finalizou sua thread.")